from .models import User
import re


def is_valid_email(email):
    # Regular expression for a basic email validation
    email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    return bool(re.match(email_pattern, email))


def filter_valid_emails(email_list):
    return [email for email in email_list if is_valid_email(email)]


def get_wonen_medewerkers_email_list():
    from web.organizations.statics import FEDERATION_TYPE_ADW
    from web.organizations.models import Federation
    federation = Federation.objects.filter(
        organization__federation_type=FEDERATION_TYPE_ADW,
    )
    if federation and not federation.first().main_email:
        return list(User.objects.wonen_medewerkers().values_list('username', flat=True))
    elif federation and federation.first().main_email:
        return federation.first().main_email_list
    return []


def get_zorginstelling_medewerkers_email_list(case):
    address_list = list(set(
        list(User.objects.zorginstelling_medewerkers(case).values_list('username', flat=True)) +
        [ff for f in case.get_linked_federations() for ff in f.main_email_list]
    ))
    return address_list


def get_woningcorporatie_medewerkers_email_list(case):
    if case.woningcorporatie and not case.woningcorporatie.main_email:
        return list(User.objects.woningcorporatie_medewerkers(case).values_list('username', flat=True))
    elif case.woningcorporatie and case.woningcorporatie.main_email:
        return case.woningcorporatie.main_email_list
    return []
