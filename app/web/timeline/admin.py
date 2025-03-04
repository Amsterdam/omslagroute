from django.contrib import admin
from .models import *


@admin.register(Moment)
class MomentAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "order", "form")
    list_editable = ("order",)
