from django.test import TestCase
from django.urls import reverse
from web.cases.models import Case, CaseStatus
from web.organizations.models import Federation, Organization
from web.organizations.statics import FEDERATION_TYPE_ZORGINSTELLING
from web.profiles.models import Profile
from .models import User
from .statics import BEGELEIDER, BEHEERDER, PB_FEDERATIE_BEHEERDER
from .utils import deactivate_user, get_cases_only_linked_to_user, remove_cases_linked_to_other_users


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

    def test_profile_has_no_cases_left(self):
        deactivate_user(self.deleted_user, new_owner=self.beheerder)

        self.assertEqual(self.deleted_user.profile.cases.count(), 0)

    def test_only_linked_cases_are_handed_over(self):
        deactivate_user(self.deleted_user, new_owner=self.beheerder)

        self.assertCountEqual(
            self.beheerder.profile.cases.all(),
            [self.case_beheerder, self.case_only_deleted_user],
        )
        self.assertEqual(list(self.colleague.profile.cases.all()), [self.case_shared])
        self.assertFalse(Case.objects.filter(profile__isnull=True).exists())

    def test_deleted_user_is_not_a_linked_user(self):
        deactivate_user(self.deleted_user, new_owner=self.beheerder)

        self.assertEqual(list(self.case_shared.get_linked_users()), [self.colleague])

    def test_deactivated_user_with_cases_is_not_a_linked_user(self):
        # users deactivated in the admin still have cases in their profile
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

    def test_without_new_owner_only_linked_cases_stay_on_profile(self):
        deactivate_user(self.deleted_user)

        self.assertEqual(
            list(self.deleted_user.profile.cases.all()),
            [self.case_only_deleted_user],
        )

    def test_user_can_not_hand_over_cases_to_itself(self):
        deactivate_user(self.deleted_user, new_owner=self.deleted_user)

        self.assertEqual(
            list(self.deleted_user.profile.cases.all()),
            [self.case_only_deleted_user],
        )

    def test_federation_delete_view(self):
        self.client.force_login(self.beheerder)

        response = self.client.post(
            reverse('delete_federation_user', kwargs={'pk': self.deleted_user.id})
        )

        self.assertEqual(response.status_code, 302)
        self.deleted_user.refresh_from_db()
        self.assertFalse(self.deleted_user.is_active)
        self.assertEqual(self.deleted_user.profile.cases.count(), 0)
        self.assertIn(self.case_only_deleted_user, self.beheerder.profile.cases.all())

    def test_delete_view(self):
        beheerder = self.create_user('beheerder-adw@example.com', BEHEERDER, federation=False)
        self.client.force_login(beheerder)

        response = self.client.post(
            reverse('delete_user', kwargs={'pk': self.deleted_user.id})
        )

        self.assertEqual(response.status_code, 302)
        self.deleted_user.refresh_from_db()
        self.assertFalse(self.deleted_user.is_active)
        self.assertEqual(
            list(self.deleted_user.profile.cases.all()),
            [self.case_only_deleted_user],
        )
        self.assertEqual(beheerder.profile.cases.count(), 0)

    def test_remove_cases_linked_to_other_users(self):
        self.deleted_user.is_active = False
        self.deleted_user.save()

        removed = remove_cases_linked_to_other_users(self.deleted_user)

        self.assertEqual(removed, 1)
        self.assertEqual(
            list(self.deleted_user.profile.cases.all()),
            [self.case_only_deleted_user],
        )
        self.assertEqual(list(self.colleague.profile.cases.all()), [self.case_shared])

    def test_admin_action_only_cleans_up_inactive_users(self):
        admin = User.objects.create(username='admin@example.com', is_staff=True, is_superuser=True)
        Profile.objects.create(user=admin)
        self.client.force_login(admin)
        inactive_user = self.create_user('pb-d@example.com', BEGELEIDER)
        inactive_user.profile.cases.add(self.case_shared)
        inactive_user.is_active = False
        inactive_user.save()

        response = self.client.post(reverse('admin:users_user_changelist'), {
            'action': 'clean_up_cases_of_inactive_users',
            '_selected_action': [inactive_user.id, self.deleted_user.id],
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(inactive_user.profile.cases.count(), 0)
        self.assertEqual(self.deleted_user.profile.cases.count(), 2)

    def test_admin_action_lists_cases_that_stay_on_profile(self):
        admin = User.objects.create(username='admin@example.com', is_staff=True, is_superuser=True)
        Profile.objects.create(user=admin)
        self.client.force_login(admin)
        self.deleted_user.is_active = False
        self.deleted_user.save()

        response = self.client.post(reverse('admin:users_user_changelist'), {
            'action': 'clean_up_cases_of_inactive_users',
            '_selected_action': [self.deleted_user.id],
        }, follow=True)

        self.assertContains(
            response,
            'niet losgekoppeld bij pb-a@example.com: cliënt id %s' % self.case_only_deleted_user.id,
        )
