from django.contrib.auth.forms import (
    AuthenticationForm as DefaultAuthenticationForm, authenticate
)
from django import forms
from django.forms import widgets
from .models import *
from django.http import HttpResponse
from web.profiles.models import Profile
from django.forms.models import inlineformset_factory
from web.organizations.models import Organization
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm as DefaultUserCreationForm
from web.forms.widgets import CheckboxSelectMultiple
from django.forms.utils import ErrorList
from django.utils.translation import ugettext_lazy as _


class FilterListForm(forms.Form):
    filter = forms.CharField(
        label='Filter lijst',
        widget=CheckboxSelectMultiple(
            choices=User.user_types,
        ),
        required=False,
    )
    search = forms.CharField(
        label=_('Zoeken'),
        required=False
    )


class FilterListFederationForm(forms.Form):
    filter = forms.MultipleChoiceField(
        label='Filter lijst',
        choices=User.user_types,
        widget=CheckboxSelectMultiple(),
        required=False,
    )
    def __init__(self, *args, **kwargs):
        user_type_choices = kwargs.pop('user_type_choices', ())
        super().__init__(*args, **kwargs)
        self.fields['filter'].choices = user_type_choices


class AuthenticationForm(DefaultAuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                pass
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'user_type',
            'federation',
        )

class FederationUserUpdateForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = (
            'user_type',
        )
    def __init__(self, *args, **kwargs):
        user_type_choices = kwargs.pop('user_type_choices', ())
        super().__init__(*args, **kwargs)
        self.fields['user_type'].choices = user_type_choices


class UserCreationForm(forms.ModelForm):
    username = forms.EmailField(
        label=_('E-mailadres (gebruikersnaam)'),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['federation'].label = 'Organisatie'

    class Meta:
        model = User
        fields = (
            'username',
            'federation',
            'user_type',
        )

class UserCreationFederationForm(forms.ModelForm):
    username = forms.EmailField(
        label=_('E-mailadres (gebruikersnaam)'),
        required=True
    )
    class Meta:
        model = User
        fields = (
            'username',
            'user_type',
        )

    def __init__(self, *args, **kwargs):
        user_type_choices = kwargs.pop('user_type_choices', ())
        super().__init__(*args, **kwargs)
        self.fields['user_type'].choices = user_type_choices


class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = Profile
        exclude = [
            'cases',
            'user',
            'organization',
        ]


ProfileFormSet = inlineformset_factory(
    parent_model=User,
    model=Profile,
    form=ProfileForm,
    can_delete=False,
    extra=1
)
