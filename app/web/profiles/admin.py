from django.contrib import admin

from django.contrib.admin.widgets import FilteredSelectMultiple
from web.cases.models import Case, Profile
from django import forms
from django.utils.translation import ugettext_lazy as _


class ProfileAdminForm(forms.ModelForm):
    cases = forms.ModelMultipleChoiceField(
        queryset=Case.objects.all(),
        widget=FilteredSelectMultiple(_('Cliënten'), is_stacked=False),
        label=_('Cliënten'),
    )

    class Meta:
        model = Profile
        fields = '__all__'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)
    form = ProfileAdminForm
