from .models import User
from django.db import transaction
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


def get_cases_only_linked_to_user(user):
    # Cases that have no other active user linked, profiles of inactive users don't count
    from web.cases.models import Case
    from web.profiles.models import Profile
    return Case.objects.filter(
        profile=user.profile,
    ).exclude(
        profile__in=Profile.objects.filter(user__is_active=True).exclude(id=user.profile.id),
    )


def remove_cases_linked_to_other_users(user):
    # Cases only linked to this user stay on the profile, so they don't end up without a profile
    cases = list(user.profile.cases.exclude(
        id__in=get_cases_only_linked_to_user(user).values_list('id', flat=True),
    ))
    user.profile.cases.remove(*cases)
    return len(cases)


def deactivate_user(user, new_owner=None):
    """
    Soft delete: the user is set to inactive and the profile is kept for historical data (case statuses etc.).
    Cases only linked to this user are handed over to new_owner, all other links to cases are removed.
    Without new_owner the cases only linked to this user stay on the profile, so they don't end up without a profile.
    """
    if new_owner == user:
        new_owner = None

    with transaction.atomic():
        profile = getattr(user, 'profile', None)
        if profile:
            cases = list(get_cases_only_linked_to_user(user))
            if new_owner:
                if cases:
                    new_owner.profile.cases.add(*cases)
                profile.cases.clear()
            else:
                remove_cases_linked_to_other_users(user)
        user.is_active = False
        user.save()
