from django.urls import reverse, reverse_lazy
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

    def get_success_url(self):
        if any(int(user_type) in [PB_FEDERATIE_BEHEERDER, FEDERATIE_BEHEERDER] for user_type in self.request.user.user_type):
            return reverse('home')
        return super().get_success_url()

    def get_queryset(self):
        queryset = super().get_queryset()
        if any(int(user_type) in [PB_FEDERATIE_BEHEERDER, FEDERATIE_BEHEERDER] for user_type in self.request.user.user_type):
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
        federation = form.save(commit=True)
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