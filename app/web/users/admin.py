from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.translation import gettext, gettext_lazy as _
from django.utils.html import mark_safe
from django.urls import reverse


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'profile_link', 'is_staff', 'is_superuser', 'user_type', 'federation')
    save_on_top = True
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Omslagroute instellingen'), {'fields': ('user_type', 'federation', 'meta')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Rechten (ongebruikt)'), {
            'classes': ('collapse',),
            'fields': ('groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_filter = ('user_type', 'federation', 'is_staff', 'is_superuser', 'is_active')

    def profile_link(self, obj):
        url = reverse('admin:%s_%s_change' % ('profiles',  'profile'),  args=[obj.profile.id])
        return mark_safe(
            """<a id="edit_related" class="button related-widget-wrapper-link add-related" href="%s?_popup=1">
            Profiel
            </a>""" % url
        )

