from django.db import models
from django.utils.translation import gettext_lazy as _
from .statics import DOCUMENT_TYPE_LIST, DOCUMENT_TYPE_DICT


class DocumentVersion(models.Model):
    document = models.ForeignKey(
        to='Document',
        verbose_name='Document',
        related_name='document_to_document_version',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    uploaded_file = models.FileField(
        verbose_name=_('Selecteer een bestand'),
        upload_to='uploads'
    )
    uploaded = models.DateTimeField(
        verbose_name=_('Initieel opgeslagen datum/tijd'),
        auto_now_add=True,
    )
    saved = models.DateTimeField(
        verbose_name=_('Opgeslagen datum/tijd'),
        auto_now=True,
    )

    def __str__(self):
        if self.document:
            return self.document.name
        return self.uploaded.strftime('%Y-%m-%d, %H:%M:%S')

    @property
    def uploaded_str(self):
        return self.uploaded.strftime('%Y-%m-%d, %H:%M:%S')

    class Meta:
        verbose_name = _('Document versie')
        verbose_name_plural = _('Document versies')
        ordering = ('-uploaded', )


class DocumentManager(models.Manager):
    def get_by_name(self, name):
        return self.filter(name__iexact=name)


class Document(models.Model):
    name = models.CharField(
        verbose_name=_('Titel van het document'),
        max_length=100,
        unique=True,
    )
    document_type = models.CharField(
        verbose_name=_('Wat voor soort document is het?'),
        max_length=50,
        default='form',
        choices=DOCUMENT_TYPE_LIST,
    )
    description = models.TextField(
        verbose_name=_('Omschrijving van het document'),
        blank=True,
        null=True,
    )

    objects = DocumentManager()

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documenten')
        ordering = ('name', )

    @property
    def document_type_path(self):
        return 'images/%s.svg' % self.document_type

    @property
    def document_type_value(self):
        return DOCUMENT_TYPE_DICT.get(self.document_type)

    def __str__(self):
        return self.name
