from django import template
from django.contrib.auth.models import Group
from web.users.auth import auth_test
register = template.Library()
from web.users.statics import *
from web.organizations.statics import FEDERATION_TYPE_WONINGCORPORATIE, FEDERATION_TYPE_ADW


@register.filter()
def is_redactie(user):
    return auth_test(user, REDACTIE)


@register.filter()
def is_begeleider(user):
    return auth_test(user, BEGELEIDER)


@register.filter()
def is_beheerder(user):
    return auth_test(user, BEHEERDER)


@register.filter()
def is_wonen_medewerker(user):
    return auth_test(user, WONEN)


@register.filter()
def is_federatie_beheerder(user):
    return auth_test(user, FEDERATIE_BEHEERDER)


@register.filter()
def is_pb_federatie_beheerder(user):
    return auth_test(user, PB_FEDERATIE_BEHEERDER)


@register.filter()
def is_woningcorporatie_medewerker(user):
    return auth_test(user, WONINGCORPORATIE_MEDEWERKER)


@register.filter()
def user_federation_type_is_woningcorporatie(user):
    return user.federation.organization.federation_type in [FEDERATION_TYPE_WONINGCORPORATIE]


@register.filter()
def user_federation_type_is_adw(user):
    return user.federation.organization.federation_type in [FEDERATION_TYPE_ADW]


@register.filter()
def is_onbekend(user):
    return auth_test(user, ONBEKEND)
