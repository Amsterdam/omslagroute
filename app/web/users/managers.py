from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from .statics import *
from web.organizations.statics import (
    FEDERATION_TYPE_ADW, 
    FEDERATION_TYPE_ZORGINSTELLING, 
    FEDERATION_TYPE_WONINGCORPORATIE
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def beheerders(self):
        queryset = self.get_queryset()
        queryset = queryset.filter(
            user_type__in=[
                BEHEERDER,
            ],
        )
        return queryset

    def federation_beheerders_by_federation(self, federation, federation_type):
        queryset = self.get_queryset()
        queryset = queryset.filter(
            user_type__in=[
                PB_FEDERATIE_BEHEERDER,
                FEDERATIE_BEHEERDER,
                WONEN,
            ],
            federation=federation,
            federation__organization__federation_type=federation_type,
        )
        return queryset

    def woningcorporatie_medewerkers(self, case):
        queryset = self.get_queryset()
        queryset = queryset.filter(
            user_type__in=[WONINGCORPORATIE_MEDEWERKER],
            federation__organization__federation_type=FEDERATION_TYPE_WONINGCORPORATIE,
            federation=case.woningcorporatie,
        )
        return queryset

    def zorginstelling_medewerkers(self, case):
        queryset = self.get_queryset()
        queryset = queryset.filter(
            user_type__in=[BEGELEIDER],
            federation__organization__federation_type=FEDERATION_TYPE_ZORGINSTELLING,
            profile__cases__in=[case],
        )
        return queryset

    def wonen_medewerkers(self):
        queryset = self.get_queryset()
        queryset = queryset.filter(
            user_type__in=[WONEN],
            federation__organization__federation_type=FEDERATION_TYPE_ADW,
        )
        return queryset

