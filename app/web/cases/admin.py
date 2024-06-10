from django.contrib import admin
from .models import *


# @admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'client_first_name',
        'client_last_name',
        'delete_request_date',
    )


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
    list_filter =   (
        'case',
        'status',
        'form',
    )


# @admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass
