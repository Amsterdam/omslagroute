from django.contrib import admin

from django.contrib.admin.widgets import FilteredSelectMultiple
from web.cases.models import Case, Profile
from django import forms
from django.utils.translation import gettext_lazy as _


class ProfileAdminForm(forms.ModelForm):
    cases = forms.ModelMultipleChoiceField(
        queryset=Case.objects.all(),
        widget=FilteredSelectMultiple(_('Cliënten'), is_stacked=False),
        label=_('Cliënten'),
        required=False,
    )

    class Meta:
        model = Profile
        fields = '__all__'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)
    form = ProfileAdminForm
    search_fields = ["user__username", "user__first_name", "user__last_name", "user__email"]
