from django.views.generic import TemplateView, RedirectView
import os
import sys
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.files.storage import default_storage
from web.timeline.models import *
from web.documents.models import *
from web.organizations.models import *
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from .utils import *
from django.contrib.auth.decorators import user_passes_test
from django.core.management import call_command
from django.http import HttpResponse
from web.users.statics import BEHEERDER
from web.organizations.statics import FEDERATION_TYPE_ZORGINSTELLING
from web.users.auth import auth_test
from web.cases.statics import *
from web.cases.models import Case, CaseStatus
from datetime import timedelta, datetime
from django.utils import timezone
import calendar


class HomePageView(TemplateView):
    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        document_list = Document.objects.all()
        floating_document_list = Document.objects.filter(moment__documents__isnull=True)
        moment_list = Moment.objects.all()
        organization_list = Organization.objects.all()

        kwargs.update({
            'document_list': document_list,
            'floating_document_list': floating_document_list,
            'moment_list': moment_list,
            'organization_list': organization_list,
        })
        return super().get_context_data(**kwargs)


class VariablesView(UserPassesTestMixin, TemplateView):
    template_name = "variables.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        list_items = [[k, v] for k, v in os.environ.items()]
        list_items = sorted(list_items)

        kwargs.update({
            'var_list': dict(list_items),
        })
        return super().get_context_data(**kwargs)


class ObjectStoreView(UserPassesTestMixin, TemplateView):
    template_name = "objectstore.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):

        documentversion_list = [{
            'name': d.uploaded_file.name,
            'generate_filename': default_storage.generate_filename(d.uploaded_file.name),
            'url': default_storage.url(default_storage.generate_filename(d.uploaded_file.name)),
            'exists': default_storage.exists(default_storage.generate_filename(d.uploaded_file.name)),
            'id': d.id
        } for d in DocumentVersion.objects.all()]

        kwargs.update({
            'objectstore_container_list': ['uploads/%s' % default_storage.get_valid_name(o) for o in default_storage.listdir('uploads')[1]],
            'documentversion_list': documentversion_list,
        })
        return super().get_context_data(**kwargs)


class SendMailView(UserPassesTestMixin, RedirectView):
    url = reverse_lazy('home')

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        mailadres = request.GET.get('mailadres')
        if mailadres:
            subject = 'Omslagroute - mail',
            from_email = settings.FROM_EMAIL
            to_emails = [mailadres]
            message = 'Het versturen van een mail werkt!'
            send_mail(subject, message, from_email, to_emails, fail_silently=False)

        return super().get(request, *args, **kwargs)


class DataView(UserPassesTestMixin, TemplateView):
    template_name = "data.html"

    def test_func(self):
        return auth_test(self.request.user, [BEHEERDER])

    def get_context_data(self, **kwargs):
        current_datetime = timezone.now()
        month = current_datetime.strftime('%m')
        year = current_datetime.strftime('%Y')
        monthrange = calendar.monthrange(int(year), int(month))
        try:
            monthrange = calendar.monthrange(int(self.request.GET.get('jaar')), int(self.request.GET.get('maand')))
            month = self.request.GET.get('maand')
            year = self.request.GET.get('jaar')
        except (ValueError, TypeError) as e:
            print(f'querystring params wrong format: {e}')

        data = []
        zorginstelling_list = Federation.objects.filter(
            organization__federation_type=FEDERATION_TYPE_ZORGINSTELLING,
        )
        all_cases = Case.objects.all()

        start_month_naive = datetime(year=int(year), month=int(month), day=1)
        start_month = timezone.make_aware(start_month_naive)
        end_month_naive = datetime(year=int(year), month=int(month), day=monthrange[1]) + timedelta(days=1)
        end_month = timezone.make_aware(end_month_naive)

        next_month = end_month.strftime('?jaar=%Y&maand=%m') if end_month < timezone.now() else None
        prev_month = (start_month - timedelta(days=1)).strftime('?jaar=%Y&maand=%m')

        casestatus_period = CaseStatus.objects.filter(
            created__gt=start_month,
            created__lte=end_month,
        )

        for zorginstelling in zorginstelling_list:
            case_list = all_cases.filter(
                profile__user__federation=zorginstelling,
            )
            case_list_period = case_list.filter(
                created__gt=start_month,
                created__lte=end_month,
            )
            casestatus_list = CaseStatus.objects.filter(
                case__in=case_list,
            )
            urgentie = casestatus_list.filter(
                form=CASE_VERSION_FORM_URGENTIE,
            )
            omklap = casestatus_list.filter(
                form=CASE_VERSION_FORM_OMKLAP,
            )
            urgentie_ingediend = urgentie.filter(
                status=CASE_STATUS_INGEDIEND,
            ).order_by('case__id', 'created').distinct('case__id')
            urgentie_goedgekeurd = urgentie.filter(
                status=CASE_STATUS_GOEDGEKEURD,
            ).order_by('case__id', '-created').distinct('case__id')
            omklap_ingediend = omklap.filter(
                status=CASE_STATUS_INGEDIEND,
            ).order_by('case__id', 'created').distinct('case__id')
            omklap_goedgekeurd = omklap.filter(
                status=CASE_STATUS_GOEDGEKEURD,
            ).order_by('case__id', '-created').distinct('case__id')
            urgentie_ingediend_period = casestatus_period.filter(
                id__in=urgentie_ingediend.values_list('id', flat=True)
            )
            urgentie_goedgekeurd_period = casestatus_period.filter(
                id__in=urgentie_goedgekeurd.values_list('id', flat=True)
            )
            omklap_ingediend_period = casestatus_period.filter(
                id__in=omklap_ingediend.values_list('id', flat=True)
            )
            omklap_goedgekeurd_period = casestatus_period.filter(
                id__in=omklap_goedgekeurd.values_list('id', flat=True)
            )

            user_list = User.objects.filter(
                federation=zorginstelling,
            )
            data.append({
                'zorginstelling': zorginstelling,
                'case_list': case_list.order_by('id', 'created').distinct('id'),
                'case_list_period': case_list_period.order_by('id', 'created').distinct('id'),
                'user_list': user_list,
                'urgentie_ingediend': urgentie_ingediend,
                'urgentie_ingediend_period': urgentie_ingediend_period,
                'urgentie_goedgekeurd': urgentie_goedgekeurd,
                'urgentie_goedgekeurd_period': urgentie_goedgekeurd_period,
                'omklap_ingediend': omklap_ingediend,
                'omklap_ingediend_period': omklap_ingediend_period,
                'omklap_goedgekeurd': omklap_goedgekeurd,
                'omklap_goedgekeurd_period': omklap_goedgekeurd_period,
            })

        kwargs.update({
            'zorginstelling_list': data,
            'all_cases': all_cases,
            'start_month': start_month,
            'next_month': next_month,
            'prev_month': prev_month,
        })
        return super().get_context_data(**kwargs)


@user_passes_test(lambda u: u.is_superuser)
def dumpdata(request):
    sysout = sys.stdout
    fname = "%s-%s.json" % ('omslagroute', settings.SOURCE_COMMIT.strip())
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=%s' % fname

    sys.stdout = response
    call_command('dumpdata', 'organizations', 'documents', 'timeline', '--indent=4')
    sys.stdout = sysout

    return response
