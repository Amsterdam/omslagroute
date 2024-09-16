from .models import Alert
from django.utils import timezone


def alerts_processor(request):
    alerts = Alert.objects.filter(start_time__lte=timezone.now(), end_time__gte=timezone.now())
    return {'alerts': alerts}
