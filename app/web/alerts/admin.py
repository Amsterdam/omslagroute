from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active_boolean', 'start_time', 'end_time', 'message',)
    search_fields = ('message',)

    # Display boolean checkmark instead of True/False
    def is_active_boolean(self, obj):
        return obj.is_active()

    is_active_boolean.boolean = True  # This tells Django to use checkmarks/crosses
    is_active_boolean.short_description = 'Active'  # Optional, to rename the column
