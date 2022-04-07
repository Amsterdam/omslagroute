from django import template
from ..models import CaseStatus 
from web.forms.utils import get_rules_reversed as rules_reversed
from ..statics import CASE_STATUS_WONINGCORPORATIE_GOEDGEKEURD
from django.shortcuts import get_object_or_404
register = template.Library()


@register.simple_tag()
def case_data(case, fields, *args, **kwargs):
    return case.to_dict(fields)


@register.simple_tag()
def case_form_data(case, organization, form, *args, **kwargs):
    if case and organization and form:
        return organization.get_case_form_data(case, form)
    return []


@register.simple_tag()
def case_data_by_field_name(data, field_name, rules_reversed={}, *args, **kwargs):
    if rules_reversed.get(field_name, []):
        if data.get(rules_reversed.get(field_name, [])[0], {}).get('raw') not in rules_reversed.get(field_name, [])[1]:
            return False
    return data.get(field_name, {})


@register.simple_tag()
def get_case_versions(versions, key, *args, **kwargs):
    if not versions:
        return False
    return versions.get(key)


@register.simple_tag()
def get_case_status_list(case, form, *args, **kwargs):
    case_status_list = CaseStatus.objects.filter(
        case=case,
        form=form,
        status=CASE_STATUS_WONINGCORPORATIE_GOEDGEKEURD,
    )
    return case_status_list

@register.simple_tag()
def get_rules_reversed(form_cnfig, *args, **kwargs):
    return rules_reversed(form_cnfig)


@register.simple_tag()
def get_document_by_id(id, *args, **kwargs):
    from web.cases.models import Document
    document = get_object_or_404(Document, id=id.value)
    return document
