from django import forms
from django.forms import widgets
from django.forms.widgets import RadioSelect
from django.forms import ValidationError
from .models import *
from django.utils.translation import gettext_lazy as _
from django.forms.models import inlineformset_factory
from django.urls import reverse_lazy
from django.utils.html import mark_safe
from web.timeline.models import Moment
from web.forms.widgets import CheckboxSelectMultiple


class DocumentVersionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['uploaded_file'].label = "Selecteer een bestand"

    class Meta:
        model = DocumentVersion
        exclude = ()
        widgets = {
            'uploaded_file': forms.FileInput(attrs={'id': 'file-upload', 'accept':'image/*,.doc,.docx,.xls,.xlsx,.pdf', 'required': 'required'}),
            'document': forms.HiddenInput,
        }


class DocumentForm(forms.ModelForm):
    moment_list = forms.ModelMultipleChoiceField(
        label=_('Selecteer een processtap'),
        queryset=Moment.objects.all(),
        widget=CheckboxSelectMultiple(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        self.empty_label=None
        self.fields['name'].label = "Wat is de titel van het document?"
        self.fields['description'].label = "Waar wordt dit document voor gebruikt?"
        self.fields['document_type'].label = "Om wat voor soort document gaat het?"

        if self.instance.id and self.instance.moment_set.all():
            self.fields['moment_list'].initial = self.instance.moment_set.all()

    def clean_name(self):
        data = self.cleaned_data['name']
        existing_names = Document.objects.get_by_name(name=data)
        if existing_names and existing_names[0].id != self.instance.id:
            url = reverse_lazy('add_document_version_to_document', kwargs={'document': existing_names[0].id})
            raise ValidationError(
                _(mark_safe('Deze naam wordt al gebruikt in een ander document. '
                            'Je kan <a href="%s">hier</a> een versie toe te voegen aan het bestaande document' % url)),
                code='invalid',
            )
        return data

    class Meta:
        model = Document
        exclude = ()
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': ' ','autofocus': 'true'}),
            'document_type': forms.RadioSelect(attrs={'class': 'form-field__radio'})
        }


DocumentVersionFormSet = inlineformset_factory(
    parent_model=Document,
    model=DocumentVersion,
    form=DocumentVersionForm,
    can_delete=False,
    extra=1
)
