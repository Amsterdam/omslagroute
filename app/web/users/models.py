from django.contrib.auth.models import AbstractBaseUser, AbstractUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from .managers import UserManager
from .statics import USER_TYPES, USER_TYPES_DICT, USER_TYPES_ACTIVE, USER_TYPES_FEDERATIE
from django.db import models
from django import forms
from django.forms import widgets
from django.contrib.postgres.fields import JSONField



class User(AbstractUser):
    user_types = [ut for ut in USER_TYPES if ut[0] in USER_TYPES_ACTIVE]
    federation_user_types = [ut for ut in USER_TYPES if ut[0] in USER_TYPES_FEDERATIE]

    user_type = models.PositiveSmallIntegerField(
        verbose_name=_('Gebruiker rol'),
        choices=user_types,
        default=6,
    )
    federation = models.ForeignKey(
        to='organizations.Federation',
        related_name='user_list',
        verbose_name=_('Federatie'),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    meta = JSONField(
        verbose_name=_('Meta'),
        blank=True,
        null=True,
    )

    objects = UserManager()

    @property
    def name(self):
        if self.first_name and self.last_name:
            return '%s %s' % (
                self.first_name,
                self.last_name,
            )
        return self.username

    @property
    def user_type_value(self):
        return USER_TYPES_DICT[self.user_type]

    class Meta:
        verbose_name = _('Gebruiker')
        verbose_name_plural = _("Gebruikers")
