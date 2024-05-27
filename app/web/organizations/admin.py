from django.contrib import admin
from .models import *
from django import forms


class OrganizationAdminForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = '__all__'
        widgets = {
            'field_restrictions': forms.CheckboxSelectMultiple
        }


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    form = OrganizationAdminForm

    class Media:
        css = {
            'all': ('static/custom_admin.css',)
        }


@admin.register(Federation)
class FederationAdmin(admin.ModelAdmin):
    list_display = ('name', 'federation_id', 'main_email', 'organization')
