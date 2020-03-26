from django.db import models
from django.utils.translation import ugettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(
        to='users.User',
        verbose_name=_('Gebruiker'),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    cases = models.ManyToManyField(
        to='cases.Case',
        verbose_name=_('Cliënten'),
        blank=True,
    )

    def __str__(self):
        if self.user:
            return self.user.username
        return str(self.id)
