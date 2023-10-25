from django.contrib.auth import logout, login
from django.http.response import HttpResponseRedirect
from django.contrib.auth.forms import (
    AuthenticationForm, authenticate
)
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import CreateView, ListView, UpdateView, FormView, TemplateView, DeleteView
from .models import *
from .forms import *
from django.urls import reverse_lazy, reverse
from web.users.auth import auth_test
from django.db import transaction
from .statics import *
from mozilla_django_oidc.views import OIDCAuthenticationRequestView as DatapuntOIDCAuthenticationRequestView
from django.core.paginator import Paginator
from mozilla_django_oidc.utils import (
    absolutify
)
from web.cases.models import Case
from django.db.models import Count, Q
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
import sendgrid
from sendgrid.helpers.mail import Mail
from django.template.loader import render_to_string

try:
    from urllib.parse import urlencode
except ImportError:
    # Python < 3
    from urllib import urlencode

from mozilla_django_oidc.views import get_next_url, get_random_string


# legacy dev only
def generic_logout(request):
    logout(request)
    messages.add_message(request, messages.INFO, 'Je bent uitgelogd')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# legacy dev only
def generic_login(request):
    if request.method == 'POST' and 'is_top_login_form' in request.POST:
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                login(request, user)
                if any(user_type in [BEGELEIDER, PB_FEDERATIE_BEHEERDER] for user_type in user.user_type_values):
                    return HttpResponseRedirect(reverse('cases_by_profile'))
                return HttpResponseRedirect(request.POST.get('next', '/'))
    messages.add_message(request, messages.ERROR, 'Er is iets mis gegaan met het inloggen')
    return HttpResponseRedirect('%s#login' % (request.POST.get('next', '/')))


class UserList(UserPassesTestMixin, TemplateView):
    template_name = 'users/user_list_page.html'
    http_method_names = ['get']

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

        # Convert the "USER_TYPES_ACTIVE" list to a list of strings
        user_types_active_str_list = [str(item) for item in USER_TYPES_ACTIVE]

        # Initialize filter_list with USER_TYPES_ACTIVE if no filter is provided
        filter_list = self.request.GET.getlist('filter', default=user_types_active_str_list)

        # Remove empty strings from filter_list
        filter_list = [f for f in filter_list if f]

        search = self.request.GET.get('search', '')

        # Create a Q object for user_type__contains filter
        filter_q = Q()
        for item in filter_list:
            filter_q |= Q(user_type__contains=item)

        # Apply search filtering
        if search:
            search_q = Q()
            for s in search.split():
                search_q |= (Q(first_name__icontains=s) |
                            Q(last_name__icontains=s) |
                            Q(email__icontains=s))
            object_list = User.objects.filter(filter_q & search_q)
        else:
            object_list = User.objects.filter(filter_q)

        # Sort by user_type using a custom list
        object_list = [[o, [USER_TYPES_ACTIVE.index(value) for value in o.user_type_values]] for o in object_list]
        object_list = sorted(object_list, key=lambda o: o[1])
        object_list = [o[0] for o in object_list]

        # Pagination
        paginator = Paginator(object_list, 20)
        page = self.request.GET.get('page', 1)
        object_list = paginator.get_page(page)

        # Create the filter parameters string
        filter_params = '&filter='.join(filter_list) if filter_list else ''

        # Update the context data
        form = FilterListForm(self.request.GET)
        kwargs.update({
            'object_list': object_list,
            'form': form,
            'filter_params': filter_params,
        })

        return kwargs

    def test_func(self):
        return auth_test(self.request.user, [BEHEERDER])


class FederationUserList(UserPassesTestMixin, TemplateView):
    template_name = 'users/federation_user_list_page.html'
    form_class = FilterListFederationForm
    http_method_names = ['get']
    per_page = 20

    def get_user_type_choices(self, federation):
        if federation.organization:
            return [[str(ut), USER_TYPES_DICT[int(ut)]] for ut in federation.organization.rol_restrictions]
        return [[str(ut[0]), ut[1]] for ut in User.user_types if ut[0] in [ONBEKEND, FEDERATIE_BEHEERDER]]

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

        # Get user's federation and its role restrictions
        federation = self.request.user.federation
        user_type_choices = self.get_user_type_choices(federation)

        user_types_federatie = [ut[0] for ut in user_type_choices]

        filter_list = self.request.GET.getlist('filter', default=user_types_federatie)

        # Remove empty strings from filter_list
        filter_list = [f for f in filter_list if f]

        search = self.request.GET.get('search', '')

        federation_q = Q(federation=federation)

        # Create a Q object for user_type__contains filter
        filter_q = Q()
        for item in filter_list:
            filter_q |= Q(user_type__contains=item)

        # Apply search filtering
        if search:
            search_q = Q()
            for s in search.split():
                search_q |= (Q(first_name__icontains=s) |
                            Q(last_name__icontains=s) |
                            Q(email__icontains=s))
            object_list = User.objects.filter(filter_q & search_q & federation_q)
        else:
            object_list = User.objects.filter(filter_q & federation_q)

        object_list = [[o, [USER_TYPES_ACTIVE.index(value) for value in o.user_type_values]] for o in object_list]
        object_list = sorted(object_list, key=lambda o: o[1])
        object_list = [o[0] for o in object_list]

        # Pagination
        paginator = Paginator(object_list, self.per_page)
        page = self.request.GET.get('page', 1)
        object_list = paginator.get_page(page)

        # Create the filter parameters string
        filter_params = '&filter='.join(filter_list) if filter_list else ''

        # Update the context data
        form = FilterListFederationForm(self.request.GET, user_type_choices=user_type_choices)
        kwargs.update({
            'object_list': object_list,
            'form': form,
            'filter_params': filter_params,
        })

        return kwargs

    def test_func(self):
        return auth_test(self.request.user, [PB_FEDERATIE_BEHEERDER, FEDERATIE_BEHEERDER, WONEN])


class UserUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    template_name_suffix = '_update_form'
    form_class = UserUpdateForm
    success_url = reverse_lazy('user_list')

    def get_success_url(self):
        if self.request.POST.get('next'):
            return self.request.POST.get('next')
        return self.success_url

    def test_func(self):
        return auth_test(self.request.user, BEHEERDER)

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, "Gebruiker %s is aangepast" % self.object.username)
        return super().form_valid(form)


class FederationUserUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    template_name_suffix = '_federation_update_form'
    form_class = FederationUserUpdateForm
    success_url = reverse_lazy('federation_user_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user_type_choices = [ut for ut in User.user_types if ut[0] in [ONBEKEND, FEDERATIE_BEHEERDER]]
        if self.request.user.federation.organization:
            user_type_choices = [[ut, USER_TYPES_DICT[int(ut)]] for ut in self.request.user.federation.organization.rol_restrictions]
        kwargs.update({
            'user_type_choices': user_type_choices
        })
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(federation=self.request.user.federation)
        return queryset

    def test_func(self):
        return auth_test(self.request.user, [PB_FEDERATIE_BEHEERDER, FEDERATIE_BEHEERDER, WONEN])

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, "Gebruiker %s is aangepast" % self.object.username)
        return super().form_valid(form)


class UserCreationView(UserPassesTestMixin, CreateView):
    model = User
    template_name_suffix = '_create_form'
    form_class = UserCreationForm
    success_url = reverse_lazy('user_list')

    def test_func(self):
        return auth_test(self.request.user, BEHEERDER)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = user.username
        user.save()
        profile = Profile()
        profile.user = user
        profile.save()

        if settings.SENDGRID_KEY:
            current_site = get_current_site(self.request)
            sg = sendgrid.SendGridAPIClient(settings.SENDGRID_KEY)
            data = {
                'creator': self.request.user,
                'user': user,
                'user_type': user.user_type_names,
                'url': 'https://%s' % current_site.domain,
            }
            body = render_to_string('users/mail/to_new_user.txt', data)
            email = Mail(
                from_email='no-reply@%s' % current_site.domain,
                to_emails=user.username,
                subject='Omslagroute - je account aangemaakt',
                plain_text_content=body
            )
            sg.send(email)

        messages.add_message(self.request, messages.INFO, "Gebruiker %s is aangemaakt en heeft een e-mail ontvangen" % user.username )
        return super().form_valid(form)


class UserCreationFederationView(UserPassesTestMixin, CreateView):
    model = User
    template_name_suffix = '_federation_create_form'
    form_class = UserCreationFederationForm
    success_url = reverse_lazy('federation_user_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user_type_choices = [ut for ut in User.user_types if ut[0] in [ONBEKEND, FEDERATIE_BEHEERDER]]
        if self.request.user.federation.organization:
            user_type_choices = [[ut, USER_TYPES_DICT[int(ut)]] for ut in self.request.user.federation.organization.rol_restrictions]
        kwargs.update({
            'user_type_choices': user_type_choices
        })
        return kwargs

    def test_func(self):
        return auth_test(self.request.user, [PB_FEDERATIE_BEHEERDER, FEDERATIE_BEHEERDER, WONEN])

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = user.username
        user.federation = self.request.user.federation
        user.save()
        profile = Profile()
        profile.user = user
        profile.save()
        if settings.SENDGRID_KEY:
            current_site = get_current_site(self.request)
            sg = sendgrid.SendGridAPIClient(settings.SENDGRID_KEY)
            data = {
                'creator': self.request.user,
                'user': user,
                'user_type': user.user_type_names,
                'url': 'https://%s' % current_site.domain,
            }
            body = render_to_string('users/mail/to_new_user.txt', data)
            email = Mail(
                from_email='no-reply@%s' % current_site.domain,
                to_emails=user.username,
                subject='Omslagroute - je account aangemaakt',
                plain_text_content=body
            )
            sg.send(email)

        messages.add_message(self.request, messages.INFO, "Gebruiker %s is aangemaakt en heeft een e-mail ontvangen" % user.username)
        return super().form_valid(form)


class UserDelete(UserPassesTestMixin, DeleteView):
    model = User
    template_name_suffix = '_delete'
    success_url = reverse_lazy('user_list')

    def get_success_url(self):
        if self.request.POST.get('next'):
            return self.request.POST.get('next')
        return self.success_url

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        cases = Case.objects.all()
        cases = cases.annotate(num_profiles=Count('profile'))
        cases = cases.filter(num_profiles=1)
        cases = cases.filter(profile=self.object.profile)
        kwargs.update({
            'cases': cases,
        })
        return kwargs

    def test_func(self):
        return auth_test(self.request.user, BEHEERDER)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.profile.delete()
        return super().delete(request, *args, **kwargs)


class UserFederationDelete(UserPassesTestMixin, DeleteView):
    model = User
    template_name_suffix = '_federation_delete'
    success_url = reverse_lazy('federation_user_list')

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        cases = Case.objects.all()
        cases = cases.annotate(num_profiles=Count('profile'))
        cases = cases.filter(num_profiles=1)
        cases = cases.filter(profile=self.object.profile)
        kwargs.update({
            'cases': cases,
        })
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(federation=self.request.user.federation)
        return queryset

    def test_func(self):
        return auth_test(self.request.user, [PB_FEDERATIE_BEHEERDER, FEDERATIE_BEHEERDER, WONEN])


class OIDCAuthenticationRequestView(DatapuntOIDCAuthenticationRequestView):
    def get(self, request):
        """OIDC client authentication initialization HTTP endpoint"""
        state = get_random_string(self.get_settings('OIDC_STATE_SIZE', 32))
        redirect_field_name = self.get_settings('OIDC_REDIRECT_FIELD_NAME', 'next')
        reverse_url = self.get_settings('OIDC_AUTHENTICATION_CALLBACK_URL',
                                        'oidc_authentication_callback')

        params = {
            'response_type': 'code',
            'scope': self.get_settings('OIDC_RP_SCOPES', 'openid email'),
            'client_id': self.OIDC_RP_CLIENT_ID,
            'redirect_uri': absolutify(
                request,
                reverse(reverse_url)
            ),
            # 'redirect_uri': 'https://acc.omslagroute.amsterdam.nl%s' % reverse(reverse_url),
            'state': state,
        }

        params.update(self.get_extra_params(request))

        if self.get_settings('OIDC_USE_NONCE', True):
            nonce = get_random_string(self.get_settings('OIDC_NONCE_SIZE', 32))
            params.update({
                'nonce': nonce
            })
            request.session['oidc_nonce'] = nonce

        request.session['oidc_states'] = {state:{'nonce':None}}
        request.session['oidc_login_next'] = get_next_url(request, redirect_field_name)

        query = urlencode(params)
        redirect_url = '{url}?{query}'.format(url=self.OIDC_OP_AUTH_ENDPOINT, query=query)
        return HttpResponseRedirect(redirect_url)
