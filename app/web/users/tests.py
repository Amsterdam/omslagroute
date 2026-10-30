from unittest.mock import patch

from django.core import mail
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from web.cases.models import Case, CaseStatus
from web.organizations.models import Federation, Organization
from web.organizations.statics import FEDERATION_TYPE_ZORGINSTELLING
from web.profiles.models import Profile
from .auth import OIDCAuthenticationBackend
from .models import User
from .statics import BEGELEIDER, BEHEERDER, PB_FEDERATIE_BEHEERDER
from .utils import deactivate_user, get_cases_only_linked_to_user


class DeactivateUserTestCase(TestCase):
    def setUp(self):
        organization = Organization.objects.create(
            name='Zorginstelling',
            federation_type=FEDERATION_TYPE_ZORGINSTELLING,
        )
        self.federation = Federation.objects.create(
            name='Zorginstelling',
            federation_id='zorginstelling',
            organization=organization,
        )
        self.beheerder = self.create_user('beheerder@example.com', PB_FEDERATIE_BEHEERDER)
        self.deleted_user = self.create_user('pb-a@example.com', BEGELEIDER)
        self.colleague = self.create_user('pb-c@example.com', BEGELEIDER)

        self.case_only_deleted_user = Case.objects.create(client_first_name='Alleen')
        self.case_shared = Case.objects.create(client_first_name='Gedeeld')
        self.case_beheerder = Case.objects.create(client_first_name='Beheerder')

        self.deleted_user.profile.cases.add(self.case_only_deleted_user, self.case_shared)
        self.colleague.profile.cases.add(self.case_shared)
        self.beheerder.profile.cases.add(self.case_beheerder)

    def create_user(self, username, user_type, federation=True):
        user = User.objects.create(
            username=username,
            user_type=[str(user_type)],
            federation=self.federation if federation else None,
        )
        Profile.objects.create(user=user)
        return user

    def test_cases_only_linked_to_user(self):
        self.assertEqual(
            list(get_cases_only_linked_to_user(self.deleted_user)),
            [self.case_only_deleted_user],
        )

    def test_profiles_of_inactive_users_do_not_count(self):
        self.colleague.is_active = False
        self.colleague.save()

        self.assertCountEqual(
            get_cases_only_linked_to_user(self.deleted_user),
            [self.case_only_deleted_user, self.case_shared],
        )

    def test_user_is_soft_deleted_and_profile_is_kept(self):
        deactivate_user(self.deleted_user, new_owner=self.beheerder)

        self.deleted_user.refresh_from_db()
        self.assertFalse(self.deleted_user.is_active)
        self.assertTrue(Profile.objects.filter(user=self.deleted_user).exists())

    def test_profile_keeps_its_cases(self):
        deactivate_user(self.deleted_user, new_owner=self.beheerder)

        self.assertCountEqual(
            self.deleted_user.profile.cases.all(),
            [self.case_only_deleted_user, self.case_shared],
        )

    def test_only_linked_cases_are_handed_over(self):
        deactivate_user(self.deleted_user, new_owner=self.beheerder)

        self.assertCountEqual(
            self.beheerder.profile.cases.all(),
            [self.case_beheerder, self.case_only_deleted_user],
        )
        self.assertEqual(list(self.colleague.profile.cases.all()), [self.case_shared])

    def test_deleted_user_is_not_a_linked_user(self):
        deactivate_user(self.deleted_user, new_owner=self.beheerder)

        self.assertEqual(list(self.case_shared.get_linked_users()), [self.colleague])

    def test_deactivated_user_is_not_a_linked_user(self):
        # users deactivated in the admin don't hand over their cases
        self.deleted_user.is_active = False
        self.deleted_user.save()

        self.assertEqual(list(self.case_shared.get_linked_users()), [self.colleague])

    def test_case_status_history_is_kept(self):
        case_status = CaseStatus.objects.create(
            case=self.case_shared,
            profile=self.deleted_user.profile,
        )

        deactivate_user(self.deleted_user, new_owner=self.beheerder)

        case_status.refresh_from_db()
        self.assertEqual(case_status.profile.user, self.deleted_user)

    def test_without_new_owner_no_cases_are_handed_over(self):
        deactivate_user(self.deleted_user)

        self.deleted_user.refresh_from_db()
        self.assertFalse(self.deleted_user.is_active)
        self.assertEqual(list(self.beheerder.profile.cases.all()), [self.case_beheerder])

    def test_user_can_not_hand_over_cases_to_itself(self):
        deactivate_user(self.deleted_user, new_owner=self.deleted_user)

        self.assertCountEqual(
            self.deleted_user.profile.cases.all(),
            [self.case_only_deleted_user, self.case_shared],
        )

    def test_federation_delete_view(self):
        self.client.force_login(self.beheerder)

        response = self.client.post(
            reverse('delete_federation_user', kwargs={'pk': self.deleted_user.id})
        )

        self.assertEqual(response.status_code, 302)
        self.deleted_user.refresh_from_db()
        self.assertFalse(self.deleted_user.is_active)
        self.assertIn(self.case_only_deleted_user, self.beheerder.profile.cases.all())
        self.assertNotIn(self.case_shared, self.beheerder.profile.cases.all())

    def test_delete_view(self):
        beheerder = self.create_user('beheerder-adw@example.com', BEHEERDER, federation=False)
        self.client.force_login(beheerder)

        response = self.client.post(
            reverse('delete_user', kwargs={'pk': self.deleted_user.id})
        )

        self.assertEqual(response.status_code, 302)
        self.deleted_user.refresh_from_db()
        self.assertFalse(self.deleted_user.is_active)
        self.assertEqual(beheerder.profile.cases.count(), 0)

    def test_remove_invited_user_hands_over_case_when_only_inactive_users_are_left(self):
        self.deleted_user.is_active = False
        self.deleted_user.save()
        self.client.force_login(self.beheerder)

        response = self.client.post(
            reverse('case_remove_invited_users', kwargs={'pk': self.case_shared.id}),
            {'user_list': [self.colleague.id]},
        )

        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.case_shared, self.colleague.profile.cases.all())
        self.assertIn(self.case_shared, self.beheerder.profile.cases.all())


@override_settings(EMAIL_HOST_USER='local')
class UserMailTestCase(TestCase):
    def setUp(self):
        self.federation = Federation.objects.create(
            name='Zorginstelling',
            federation_id='zorginstelling',
            organization=Organization.objects.create(
                name='Zorginstelling',
                federation_type=FEDERATION_TYPE_ZORGINSTELLING,
            ),
        )
        self.beheerder = User.objects.create(
            username='beheerder@example.com',
            user_type=[str(BEHEERDER)],
            federation=self.federation,
        )
        Profile.objects.get_or_create(user=self.beheerder)

    def test_account_created_by_beheerder(self):
        self.client.force_login(self.beheerder)

        self.client.post(
            reverse('create_user'),
            {
                'username': 'nieuw@example.com',
                'federation': self.federation.id,
                'user_type': [str(BEGELEIDER)],
            },
        )

        message = mail.outbox[-1]
        self.assertEqual(message.subject, 'Omslagroute - je account is aangemaakt')
        self.assertEqual(message.to, ['nieuw@example.com'])
        self.assertIn('<strong>Naar de Omslagroute</strong>', message.alternatives[0][0])
        self.assertNotIn('Je moet ingelogd zijn', message.body)

    @patch('web.users.auth.MozillaOIDCAuthenticationBackend.create_user')
    def test_first_login_notifies_beheerders(self, create_user):
        create_user.return_value = User.objects.create(username='nieuw@example.com')
        backend = OIDCAuthenticationBackend.__new__(OIDCAuthenticationBackend)
        backend.UserModel = User
        backend.request = RequestFactory().get('/')

        backend.create_user({'federation': 'zorginstelling'})

        message = mail.outbox[-1]
        self.assertEqual(message.subject, 'Omslagroute - gebruiker aangemaakt')
        self.assertEqual(message.to, ['beheerder@example.com'])
        self.assertIn('<strong>Gebruiker beheren</strong>', message.alternatives[0][0])
