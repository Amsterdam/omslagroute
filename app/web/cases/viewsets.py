from rest_framework import viewsets, generics
from .models import CaseStatus, Case
from .statics import CASE_STATUS_INGEDIEND, CASE_STATUS_DICT
from .serializers import CaseStatusSerializer, CaseDossierNrSerializer
from django.contrib.auth.mixins import UserPassesTestMixin
from web.users.statics import WONEN, WONINGCORPORATIE_MEDEWERKER
from web.forms.statics import FORMS_BY_SLUG
from web.users.auth import auth_test
from web.users.utils import get_zorginstelling_medewerkers_email_list
from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail


class CaseStatusUpdateViewSet(UserPassesTestMixin, viewsets.ModelViewSet):
    queryset = CaseStatus.objects.all()
    serializer_class = CaseStatusSerializer

    def test_func(self):
        return auth_test(self.request.user, [WONEN, WONINGCORPORATIE_MEDEWERKER]) and hasattr(self.request.user, 'profile')

    def get_queryset(self):
        filters = ['case', 'form', 'status']
        get_vars = self.request.GET
        queryset = CaseStatus.objects.filter(
            case__in=Case.objects.by_user(self.request.user).values_list('id', flat=True),
        )
        kwargs = dict(('%s__in' % f, get_vars.getlist(f)) for f in filters if get_vars.getlist(f))
        return queryset.filter(**kwargs).order_by('-created')

    def create(self, request, *args, **kwargs):
        data = {'profile': request.user.profile.id}
        data.update(request.data)
        if data.get('status') != CASE_STATUS_INGEDIEND:
            data.update({
                'case_version': Case.objects.get(id=data.get('case')).create_version(data.get('form')).id,
            })

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        if serializer.instance.status != CASE_STATUS_INGEDIEND:
            current_site = get_current_site(request)
            form_config = FORMS_BY_SLUG.get(serializer.instance.form)
            message = render_to_string('cases/mail/case_status_to_pb.txt', {
                'case_status': serializer.instance,
                'form_name': form_config.get('title'),
                'case_form_url': 'https://%s%s' % (
                    current_site.domain,
                    reverse('update_case', kwargs={
                        'pk': serializer.instance.case.id,
                        'form_config_slug': serializer.instance.form,
                    })
                ),
            })
            email_adresses = get_zorginstelling_medewerkers_email_list(serializer.instance.case)
            if settings.EMAIL_HOST_USER and email_adresses:
                subject = 'Omslagroute - %s, status: %s' % (
                    form_config.get('title'),
                    CASE_STATUS_DICT.get(serializer.instance.status).get('current'),
                )
                from_email = settings.FROM_EMAIL
                to_emails = email_adresses
                send_mail(subject, message, from_email, to_emails, fail_silently=False)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CaseUpdateDossierNrViewSet(UserPassesTestMixin, viewsets.ViewSetMixin, generics.RetrieveUpdateAPIView):
    queryset = Case.objects.all()
    serializer_class = CaseDossierNrSerializer

    def test_func(self):
        return auth_test(self.request.user, [WONEN]) and hasattr(self.request.user, 'profile')

    def get_queryset(self):
        return Case._default_manager.by_user(user=self.request.user)