from django.db import models
from django.utils.translation import gettext_lazy as _
from web.core.models import PrintableModel
from web.forms.statics import FORMS_CHOICES

class Moment(PrintableModel):
    textile_fields = (
        'description'
    )
    name = models.CharField(
        verbose_name=_('Naam'),
        max_length=100
    )
    description = models.TextField(
        verbose_name=_('Omschrijving van het moment'),
        blank=True,
        null=True,
    )
    order = models.IntegerField(
        verbose_name=_('Sorteer'),
        default=1,
        blank=True,
        null=True,
    )
    documents = models.ManyToManyField(
        to='documents.Document',
        verbose_name=_('Documenten'),
        blank=True,
    )
    organizations = models.ManyToManyField(
        to='organizations.Organization',
        verbose_name=_('Organisaties'),
        blank=True,
    )
    form = models.CharField(
        verbose_name=_('Formulier'),
        max_length=100,
        choices=FORMS_CHOICES,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Moment')
        verbose_name_plural = _('Momenten')
        ordering = ('order',)
