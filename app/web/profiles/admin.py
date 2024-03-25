from django.contrib import admin
from .models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)
    search_fields = ["user__username", "user__first_name", "user__last_name", "user__email"]
