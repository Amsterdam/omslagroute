import unicodedata

from django.conf import settings


def generate_username(email):
    # Usernames can contain alphanumeric (ascii and unicode), _, @, +, . and -
    # characters. So we normalize it and slice at 150 characters.
    return unicodedata.normalize('NFKC', email)[:150]


def oidc_op_logout(request):
    redirect_url = request.build_absolute_uri(getattr(settings, 'LOGOUT_REDIRECT_URL', '/'))
    return '{}?post_logout_redirect_uri={}&client_id={}'.format(
        settings.OIDC_OP_LOGOUT_ENDPOINT, redirect_url, settings.OIDC_RP_CLIENT_ID
    )
