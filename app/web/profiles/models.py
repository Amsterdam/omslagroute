from django.db import models
from django.utils.translation import gettext_lazy as _


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
        related_name='profiles',  # Explicit reverse relation name
        blank=True,
    )

    @property
    def federation(self):
        return self.user.federation

    def __str__(self):
        if self.user:
            return self.user.username
        return str(self.id)
