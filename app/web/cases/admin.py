from django.contrib import admin
from .models import *
from django.db.models import Count


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client_first_name',
        'client_last_name',
        'saved',
        'created',
        'num_profiles',
        'delete_request_date',
    )
    list_select_related = False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(num_profiles=Count('profiles'))
        return queryset

    def num_profiles(self, obj):
        return obj.num_profiles

    num_profiles.admin_order_field = 'num_profiles'
    num_profiles.short_description = 'Profile connecties'


# @admin.register(CaseVersion)
class CaseVersionAdmin(CaseAdmin):
    list_display = (
        'id',
        'case',
        'version_verbose',
        'saved_by',
        'created',
        'client_first_name',
        'client_last_name',
    )


# @admin.register(CaseStatus)
class CaseStatusAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'case',
        'status',
        'created',
        'form',
        'profile',
        'case_version',
    )
    list_filter = (
        'case',
        'status',
        'form',
    )


# @admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass
