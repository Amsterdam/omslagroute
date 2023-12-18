from django.contrib.auth.forms import (
    AuthenticationForm as DefaultAuthenticationForm, authenticate
)
from django import forms
from .models import *
from web.organizations.models import Federation
from web.forms.widgets import CheckboxSelectMultiple
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
    search = forms.CharField(
        label=_('Zoeken'),
        required=False
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
        widgets = {
            'user_type': CheckboxSelectMultiple(attrs={'class': 'u-list-style-none list-container'})
        }


class FederationUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'user_type',
        )
        widgets = {
            'user_type': CheckboxSelectMultiple(attrs={'class': 'u-list-style-none list-container'})
        }

    def __init__(self, *args, **kwargs):
        user_type_choices = kwargs.pop('user_type_choices', ())
        super().__init__(*args, **kwargs)
        self.fields['user_type'].choices = user_type_choices


class UserCreationForm(forms.ModelForm):
    username = forms.EmailField(
        label=_('E-mailadres (gebruikersnaam)'),
        required=True
    )

    class Meta:
        model = User
        fields = (
            'username',
            'federation',
            'user_type',
        )
        widgets = {
            'user_type': CheckboxSelectMultiple(attrs={'class': 'u-list-style-none list-container'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['federation'].label = 'Organisatie'


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
        widgets = {
            'user_type': CheckboxSelectMultiple(attrs={'class': 'u-list-style-none list-container'})
        }

    def __init__(self, *args, **kwargs):
        user_type_choices = kwargs.pop('user_type_choices', ())
        super().__init__(*args, **kwargs)
        self.fields['user_type'].choices = user_type_choices


class ChangeFederationForm(forms.Form):
    new_federation = forms.ModelChoiceField(
        queryset=Federation.objects.all(),
        required=True,
        label=_('Nieuwe federatie'),
    )
