from django import forms
from .models import *
from .statics import *
from django.utils.translation import ugettext_lazy as _
from web.users.statics import BEHEERDER, PB_FEDERATIE_BEHEERDER, FEDERATIE_BEHEERDER, WONEN


class OrganizationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = _('Naam organisatie')
        self.fields['name_abbreviation'].label = _('Afkorting organisatie')

    class Meta:
        model = Organization
        fields = (
            'name',
            'name_abbreviation',
        )
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Naam organisatie','aria-label': 'Naam organisatie'}),
            'name_abbreviation': forms.TextInput(attrs={'placeholder': 'NIEUW','aria-label': 'Afkorting naam organisatie'}),
        }


class FederationForm(forms.ModelForm):
    class Meta:
        model = Federation
        exclude = [
            'name_abbreviation',
        ]
        widgets = {
            'main_email': forms.Textarea(
                attrs={'rows': 2},
            )
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        if any(int(user_type) in [PB_FEDERATIE_BEHEERDER, FEDERATIE_BEHEERDER, WONEN] for user_type in user.user_type):
            del self.fields['federation_id']
            del self.fields['organization']
            del self.fields['name']
        else:
            self.fields['organization'].label = _('Organisatie type')
        if user.federation.organization.federation_type in [FEDERATION_TYPE_ADW, FEDERATION_TYPE_WONINGCORPORATIE]:
            self.fields['main_email'].label = 'Centrale e-mailadres(sen) voor notificaties'
            del self.fields['name_form_validation_team']
        else:
            self.fields['main_email'].label = 'Controleurs e-mailadres(sen)'