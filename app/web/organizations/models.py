from django.db import models
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField
from web.cases.models import Case
from web.users.models import User
from web.forms.statics import FORMS_BY_SLUG
from web.forms.utils import get_sections_fields
from web.core.utils import validate_email_wrapper
from .statics import FEDERATION_TYPE_CHOICES, FEDERATION_TYPE_ZORGINSTELLING, FEDERATION_TYPE_WONINGCORPORATIE


def get_fields():
    return [[str(f.name), '%s [%s]' % (
        str(f.name),
        str(f.verbose_name),
    )] for f in Case._meta.fields]


class Organization(models.Model):
    name = models.CharField(
        verbose_name=_('Naam'),
        max_length=100
    )
    name_abbreviation = models.CharField(
        verbose_name=_('Naam afkorting'),
        max_length=4,
        blank=True,
        null=True,
    )
    federation_type = models.PositiveIntegerField(
        verbose_name=('Federatie type'),
        choices=FEDERATION_TYPE_CHOICES,
        blank=True,
        null=True,
    )
    main_email = models.EmailField(
        verbose_name=('Standaard e-mailadres'),
        max_length=100,
        blank=True,
        null=True,
    )
    field_restrictions = MultiSelectField(
        verbose_name=_('Cliënt gegevens velden'),
        help_text=_('De inhoud van een geselecteerd veld wordt zichtbaar voor deze organisatie.'),
        choices=get_fields(),
        blank=True,
        null=True,
    )
    rol_restrictions = MultiSelectField(
        verbose_name=_('Rol opties voor federatie beheerder'),
        choices=User.user_types,
        blank=True,
        null=True,
    )

    def get_case_data(self, case):
        return case.to_dict(self.field_restrictions)

    def get_case_form_data(self, case, form):
        if self.federation_type in [FEDERATION_TYPE_ZORGINSTELLING, FEDERATION_TYPE_WONINGCORPORATIE]:
            return case.to_dict()
        form_sections = FORMS_BY_SLUG.get(form, {}).get('sections', [])
        fields = [f for f in self.field_restrictions if f in get_sections_fields(form_sections)]
        return case.to_dict(fields)

    @property
    def abbreviation(self):
        if self.name_abbreviation:
            return self.name_abbreviation
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Organisatie')
        verbose_name_plural = _('Organisaties')
        ordering = ('name',)


class Federation(models.Model):
    name = models.CharField(
        verbose_name=_('Naam'),
        max_length=100,
    )
    federation_id = models.CharField(
        verbose_name=_('Federatie id'),
        max_length=100,
        unique=True,
    )
    name_abbreviation = models.CharField(
        verbose_name=_('Naam afkorting'),
        max_length=4,
        blank=True,
        null=True,
    )
    name_form_validation_team = models.CharField(
        verbose_name=('Naam controle afdeling'),
        max_length=100,
        blank=True,
        null=True,
    )
    main_email = models.TextField(
        verbose_name=('Standaard e-mailadres(sen)'),
        help_text=_('Als je meerdere e-mailadressen wil gebruiken, kun je dat doen door ze met een komma te scheiden.'),
        blank=True,
        null=True,
    )
    organization = models.ForeignKey(
        to='Organization',
        verbose_name=('Organisatie'),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    @property
    def abbreviation(self):
        if self.name_abbreviation:
            return self.name_abbreviation
        return self.name

    @property
    def main_email_list(self):
        if self.main_email:
            return [e.strip() for e in self.main_email.split(',') if validate_email_wrapper(e.strip())]
        return []

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Federatie')
        verbose_name_plural = _('Federaties')
        ordering = ('name',)
