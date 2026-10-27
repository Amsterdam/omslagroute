from django.urls import reverse, reverse_lazy
from django.db import transaction
from django.http import HttpResponseRedirect
from .forms import *
from web.users.auth import auth_test
from django.forms import modelformset_factory
from django.shortcuts import render
from web.users.auth import user_passes_test
from web.users.statics import BEHEERDER, PB_FEDERATIE_BEHEERDER, FEDERATIE_BEHEERDER, WONEN
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.contrib import messages
from web.organizations.statics import FEDERATION_TYPE_WONINGCORPORATIE


@user_passes_test(auth_test, user_type=BEHEERDER)
def manage_organizations(request):
    organization_formset = modelformset_factory(Organization, form=OrganizationForm, extra=1, can_delete=True)
    if request.method == 'POST':
        formset = organization_formset(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            instances = formset.save()
            for instance in instances:
                instance.save()
            for object in formset.deleted_objects:
                object.delete()
            return HttpResponseRedirect(reverse('manage_organizations'))

    else:
        formset = organization_formset()
    return render(request, 'organizations/manage_organizations.html', {
        'formset': formset,
    })


class FederationListView(UserPassesTestMixin, ListView):
    model = Federation
    template_name_suffix = '_list_page'

    def test_func(self):
        return auth_test(self.request.user, [BEHEERDER]) and hasattr(self.request.user, 'profile')


class FederationCreateView(UserPassesTestMixin, CreateView):
    model = Federation
    form_class = FederationForm
    template_name_suffix = '_create_form'
    success_url = reverse_lazy('federation_list')

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def test_func(self):
        return auth_test(self.request.user, [BEHEERDER]) and hasattr(self.request.user, 'profile')

    def form_valid(self, form):
        federation = form.save(commit=True)
        messages.add_message(self.request, messages.INFO, "De organisatie '%s' is aangemaakt." % federation.name)
        return super().form_valid(form)


class FederationUpdateView(UserPassesTestMixin, UpdateView):
    model = Federation
    form_class = FederationForm
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('federation_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_users"] = self.object.user_list.filter(is_active=True)
        if 'district_email_form' not in context:
            district_email_form = self.get_district_email_form()
            if district_email_form is not None:
                context['district_email_form'] = district_email_form
        return context

    def get_district_email_form(self):
        if (
            not self.object.organization
            or self.object.organization.federation_type != FEDERATION_TYPE_WONINGCORPORATIE
        ):
            return None

        form_kwargs = {'instance': self.object}
        if self.request.method == 'POST':
            form_kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return StadsdeelEmailForm(**form_kwargs)

    def get_success_url(self):
        if any(user_type in [PB_FEDERATIE_BEHEERDER, FEDERATIE_BEHEERDER] for user_type in self.request.user.user_type_values):
            return reverse('home')
        return super().get_success_url()

    def get_queryset(self):
        queryset = super().get_queryset()
        if BEHEERDER in self.request.user.user_type_values:
            pk = self.kwargs.get('pk')
            return queryset.filter(id=pk)

        if any(user_type in [PB_FEDERATIE_BEHEERDER, FEDERATIE_BEHEERDER] for user_type in self.request.user.user_type_values):
            queryset = queryset.filter(
                id=self.request.user.federation.id,
            )
        return queryset

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def test_func(self):
        return auth_test(self.request.user, [BEHEERDER, PB_FEDERATIE_BEHEERDER, FEDERATIE_BEHEERDER, WONEN]) and hasattr(self.request.user, 'profile')

    def form_valid(self, form):
        district_email_form = self.get_district_email_form()
        if district_email_form is not None and not district_email_form.is_valid():
            return self.render_to_response(self.get_context_data(
                form=form,
                district_email_form=district_email_form,
            ))

        with transaction.atomic():
            federation = form.save(commit=True)
            if district_email_form is not None:
                district_email_form.instance = federation
                district_email_form.save()
        messages.add_message(self.request, messages.INFO, "De organisatie '%s' is opgeslagen." % federation.name)
        return super().form_valid(form)


class FederationDeleteView(UserPassesTestMixin, DeleteView):
    model = Federation
    template_name_suffix = '_delete_form'
    success_url = reverse_lazy('federation_list')

    def test_func(self):
        return auth_test(self.request.user, [BEHEERDER]) and hasattr(self.request.user, 'profile')

    def form_valid(self, form):
        federation = form.save(commit=True)
        messages.add_message(self.request, messages.INFO, "De organisatie '%s' is opgeslagen." % federation.name)
        return super().form_valid(form)