from django import forms
from .models import *
from django.utils.translation import gettext_lazy as _
from web.documents.widgets import *
from django.forms.widgets import *


class MomentForm(forms.ModelForm):
    # name = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = _('Naam processtap')
        self.fields['description'].label = _('Omschrijving processtap')

    class Meta:
        model = Moment
        fields = ('name',
                  'order',
                  'description',
                  'organizations',
        )
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': ' ','autofocus': 'true'}),
            'organizations': forms.CheckboxSelectMultiple(attrs={'class': 'form-field__checkbox'})
        }
