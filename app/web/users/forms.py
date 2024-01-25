from django.contrib.auth.forms import (
    AuthenticationForm as DefaultAuthenticationForm, authenticate
)
from django import forms
from .models import *
from web.profiles.models import Profile
from django.forms.models import inlineformset_factory
from web.forms.widgets import CheckboxSelectMultiple, RadioSelect
from django.utils.translation import gettext_lazy as _


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['federation'].label = 'Organisatie'
        user_type_choices = [ut for ut in USER_TYPES if ut[0] in USER_TYPES_ACTIVE]
        self.fields['user_type'] = forms.ChoiceField(
            choices=user_type_choices,
            widget=RadioSelect(attrs={'class': 'u-list-style-none list-container'}),
            label=User._meta.get_field('user_type').verbose_name
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
        self.fields['user_type'] = forms.ChoiceField(
            choices=user_type_choices,
            widget=RadioSelect(attrs={'class': 'u-list-style-none list-container'}),
            label=User._meta.get_field('user_type').verbose_name
        )


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['federation'].label = 'Organisatie'
        user_type_choices = [ut for ut in USER_TYPES if ut[0] in USER_TYPES_ACTIVE]
        self.fields['user_type'] = forms.ChoiceField(
            choices=user_type_choices,
            widget=RadioSelect(attrs={'class': 'u-list-style-none list-container'}),
            label=User._meta.get_field('user_type').verbose_name
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
        self.fields['user_type'] = forms.ChoiceField(
            choices=user_type_choices,
            widget=RadioSelect(attrs={'class': 'u-list-style-none list-container'}),
            label=User._meta.get_field('user_type').verbose_name
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = [
            'cases',
            'user',
            'organization',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''


ProfileFormSet = inlineformset_factory(
    parent_model=User,
    model=Profile,
    form=ProfileForm,
    can_delete=False,
    extra=1
)
