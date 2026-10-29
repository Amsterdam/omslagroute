from django import forms
from .models import *
from .statics import *
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import transaction
from web.users.statics import BEHEERDER


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
            'name': forms.TextInput(attrs={'placeholder': 'Naam organisatie', 'aria-label': 'Naam organisatie'}),
            'name_abbreviation': forms.TextInput(attrs={'placeholder': 'NIEUW', 'aria-label': 'Afkorting naam organisatie'}),
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
        # Only BEHEERDER can change Name, federation_id and Organization(type)
        if BEHEERDER not in user.user_type_values:
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


class EmailListField(forms.CharField):
    def clean(self, value):
        value = super().clean(value)
        email_field = forms.EmailField()
        emails = []
        seen = set()
        for value in value.split(','):
            if not value.strip():
                continue
            email = email_field.clean(value)
            if email.casefold() in seen:
                raise ValidationError(
                    _('Een e-mailadres kan maar één keer per stadsdeel worden ingesteld.')
                )
            seen.add(email.casefold())
            emails.append(email)
        return emails


class StadsdeelEmailForm(forms.Form):
    def __init__(self, *args, instance, **kwargs):
        kwargs.setdefault('prefix', 'district_emails')
        super().__init__(*args, **kwargs)
        self.instance = instance
        existing_emails = {}
        for district_email in instance.district_emails.all():
            existing_emails.setdefault(district_email.stadsdeel, []).append(district_email.email)

        for stadsdeel, label in STADSDEEL_CHOICES:
            self.fields[stadsdeel] = EmailListField(
                label=label,
                required=False,
                initial=', '.join(existing_emails.get(stadsdeel, [])),
                widget=forms.Textarea(attrs={'rows': 1}),
            )

    @transaction.atomic
    def save(self):
        if not self.is_valid():
            raise ValueError('The district email addresses could not be saved because the form is invalid.')

        for stadsdeel, emails in self.cleaned_data.items():
            district_emails = self.instance.district_emails.filter(stadsdeel=stadsdeel)
            district_emails.exclude(email__in=emails).delete()
            for email in emails:
                self.instance.district_emails.get_or_create(stadsdeel=stadsdeel, email=email)
