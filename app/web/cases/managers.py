from django.db import models
from web.users.statics import *
from web.forms.statics import FORMS_SLUG_BY_FEDERATION_TYPE
from web.organizations.statics import FEDERATION_TYPE_WONINGCORPORATIE, FEDERATION_TYPE_ADW
from web.profiles.models import Profile
from datetime import timedelta
from django.utils import timezone
from constance import config


class CaseManager(models.Manager):
    def by_user(self, user):
        from .models import CaseVersion
        datetime_treshold = timezone.now() - timedelta(seconds=config.CASE_DELETE_SECONDS)
        queryset = self.get_queryset()

        if PB_FEDERATIE_BEHEERDER in user.user_type_values:
            queryset = queryset.filter(
                profile__in=Profile.objects.filter(
                    user__federation=user.federation,
                )
            ).exclude(
                delete_request_date__lte=datetime_treshold
            ).order_by('-saved').distinct('id', 'saved')
            return queryset

        if BEGELEIDER in user.user_type_values:
            queryset = queryset.filter(
                id__in=user.profile.cases.all().values_list('id', flat=True)
            ).exclude(
                delete_request_date__lte=datetime_treshold
            ).order_by('-saved')
            return queryset

        if WONINGCORPORATIE_MEDEWERKER in user.user_type_values:
            queryset = queryset.filter(
                id__in=CaseVersion.objects.filter(
                    version_verbose__in=FORMS_SLUG_BY_FEDERATION_TYPE.get(
                        FEDERATION_TYPE_WONINGCORPORATIE,
                    )
                ).order_by('case').distinct().values_list('case'),
                woningcorporatie=user.federation,
            )
            return queryset

        queryset = queryset.filter(
            id__in=CaseVersion.objects.filter(
                version_verbose__in=FORMS_SLUG_BY_FEDERATION_TYPE.get(FEDERATION_TYPE_ADW)
            ).order_by('case').distinct().values_list('case'),
            delete_request_date__isnull=True,
        )
        return queryset


class CaseVersionManager(models.Manager):
    def by_user(self, user):
        from .models import Case
        queryset = self.get_queryset()

        return queryset.filter(
            case__in=Case._default_manager.by_user(user=user)
        )


class DocumentManager(models.Manager):
    def by_user(self, user):
        from .models import Case
        queryset = self.get_queryset()

        return queryset.filter(
            case__in=Case._default_manager.by_user(user=user)
        )
