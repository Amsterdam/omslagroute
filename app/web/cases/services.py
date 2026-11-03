from datetime import timedelta
from zoneinfo import ZoneInfo

from constance import config
from django.conf import settings
from django.utils import timezone

from .models import Case


def expired_delete_request_cases():
    """Cases whose delete request is older than CASE_DELETE_SECONDS."""
    datetime_treshold = timezone.now() - timedelta(seconds=config.CASE_DELETE_SECONDS)
    return Case.objects.filter(delete_request_date__lte=datetime_treshold)


def delete_date(case):
    """Date (Amsterdam time) on which the case will be deleted automatically."""
    if not case.delete_request_date:
        return None
    return timezone.localtime(
        case.delete_request_date + timedelta(seconds=config.CASE_DELETE_SECONDS),
        ZoneInfo(settings.FRONTEND_TIMEZONE),
    )


def delete_case_permanently(case):
    """
    Permanently delete a case including its versions, statuses and documents.

    Always call this per instance: Case.delete() also removes the uploaded files
    from storage, which a queryset.delete() would skip.
    """
    case.delete()
