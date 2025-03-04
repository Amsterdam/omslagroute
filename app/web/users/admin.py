from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe
from django.urls import reverse
from .forms import ChangeFederationForm
from django.shortcuts import render


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "profile_link",
        "is_staff",
        "is_superuser",
        "user_type_names",
        "federation",
        "date_joined",
        "last_login",
    )
    save_on_top = True
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Omslagroute instellingen"),
            {"fields": ("user_type", "federation", "meta")},
        ),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": ("is_active", "is_staff", "is_superuser"),
            },
        ),
        (
            _("Rechten (ongebruikt)"),
            {
                "classes": ("collapse",),
                "fields": ("groups", "user_permissions"),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_filter = ("user_type", "federation", "is_staff", "is_superuser", "is_active")
    actions = ["change_federation_action"]

    def profile_link(self, obj):
        url = reverse(
            "admin:%s_%s_change" % ("profiles", "profile"), args=[obj.profile.id]
        )
        return mark_safe(
            """<a id="edit_related" class="button related-widget-wrapper-link add-related" href="%s?_popup=1">
            Profiel
            </a>"""
            % url
        )

    def change_federation_action(self, request, queryset):
        if "action_change_federation" in request.POST:
            form = ChangeFederationForm(request.POST)
            if form.is_valid():
                new_federation = form.cleaned_data["new_federation"]
                updated = queryset.update(federation=new_federation)
                messages.success(
                    request, "{0} gebruikers zijn succesvol gewijzigd!".format(updated)
                )
                return
        else:
            form = ChangeFederationForm()

        return render(
            request,
            "users/change_federation_action.html",
            {"title": _("Wijzig federatie"), "users": queryset, "form": form},
        )

    change_federation_action.short_description = _(
        "Wijzig federatie voor geselecteerde gebruikers"
    )
