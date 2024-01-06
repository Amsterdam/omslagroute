from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField
from .managers import UserManager
from .statics import USER_TYPES, USER_TYPES_DICT, USER_TYPES_ACTIVE
from django.db import models
from django.db.models import JSONField


class User(AbstractUser):
    user_types = [ut for ut in USER_TYPES if ut[0] in USER_TYPES_ACTIVE]
    user_type = MultiSelectField(  # MultiSelectField stores vales as a comma separated string in a CharField
        verbose_name=_('Gebruiker rol'),
        choices=user_types,
        default=[6],
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
    def user_type_values(self):
        # The MultiSelectField user_type is returning a list of strings instead of integers.
        # With this property it's easier to filter.
        return [int(value) for value in self.user_type]

    @property
    def user_type_names(self):
        names = [USER_TYPES_DICT.get(value, 'Unknown') for value in self.user_type_values]
        return ", ".join(names)

    class Meta:
        verbose_name = _('Gebruiker')
        verbose_name_plural = _("Gebruikers")
