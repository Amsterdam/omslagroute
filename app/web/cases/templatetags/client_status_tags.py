from django import template
from web.forms.statics import FORMS_BY_SLUG
from ..models import CaseVersion, CaseStatus
from web.organizations.models import Organization, Federation
from web.organizations.statics import FEDERATION_TYPE_WONINGCORPORATIE, FEDERATION_TYPE_ADW
from ..statics import *
register = template.Library()


@register.simple_tag()
def client_status(client, form_key, *args, **kwargs):
    if not FORMS_BY_SLUG.get(form_key):
        return {}
    return client.status(FORMS_BY_SLUG.get(form_key).get('sections', []))


@register.simple_tag()
def client_submitted_form(client, form_key, *args, **kwargs):
    case_status = CaseStatus.objects.filter(case=client, form=form_key).order_by('-created')
    if case_status:
        return case_status[0]
    return None


@register.simple_tag()
def case_status_list_latest(case, *args, **kwargs):
    case_status_list = CaseStatus.objects.filter(
        case=case,
        status__in=[
            CASE_STATUS_INTERNE_CONTROLE,
            CASE_STATUS_INGEDIEND,
            CASE_STATUS_AFGEKEURD,
            CASE_STATUS_IN_BEHANDELING,
            CASE_STATUS_GOEDGEKEURD,
        ]
    ).order_by('-created')
    return case_status_list


@register.simple_tag()
def case_versions(case, form, *args, **kwargs):
    return case.get_versions(form)


@register.filter()
def case_status_in_concept(case_status):
    return case_status.status in IN_CONCEPT


@register.filter()
def status_verbose(status):
    return CASE_STATUS_DICT.get(status, {}).get('current')


@register.filter()
def status_template(case_status):
    return 'cases/status/%s' % CASE_STATUS_DICT.get(case_status, {}).get('template', 'empty.html')


@register.filter()
def status_class(case_status):
    return CASE_STATUS_DICT.get(case_status, {}).get('status_class')


@register.filter()
def form_verbose(form):
    return FORMS_BY_SLUG.get(form, {}).get('title')


@register.filter()
def form_federation_type(form):
    return FORMS_BY_SLUG.get(form, {}).get('federation_type')


@register.filter()
def form_list_versions(form):
    return FORMS_BY_SLUG.get(form, {}).get('list_versions')


@register.filter()
def form_organization_type_abbreviation(form):
    organization = Organization.objects.filter(
        federation_type=FORMS_BY_SLUG.get(form, {}).get('federation_type'),
    ).first()
    if organization:
        return organization.abbreviation
    return None


@register.simple_tag()
def woningcorporatie_federation(case, form):
    ft = FORMS_BY_SLUG.get(form, {}).get('federation_type')
    if ft == FEDERATION_TYPE_WONINGCORPORATIE and case.woningcorporatie:
        return case.woningcorporatie
    return None


@register.simple_tag()
def form_federation(case, form):
    ft = FORMS_BY_SLUG.get(form, {}).get('federation_type')
    federation = Federation.objects.filter(
        organization__federation_type=ft,
    ).first()
    if ft == FEDERATION_TYPE_WONINGCORPORATIE and case.woningcorporatie:
        return case.woningcorporatie
    elif ft == FEDERATION_TYPE_ADW and federation:
        return federation
    return None