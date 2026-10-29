from django.test import TestCase
from django.urls import reverse

from web.cases.models import Case
from web.organizations.models import (
    Federation,
    StadsdeelEmail,
    Organization,
)
from web.organizations.statics import FEDERATION_TYPE_WONINGCORPORATIE
from web.organizations.forms import StadsdeelEmailForm
from web.users.utils import get_woningcorporatie_medewerkers_email_list
from web.users.models import User
from web.users.statics import FEDERATIE_BEHEERDER
from web.profiles.models import Profile


class FederationDistrictEmailTestCase(TestCase):
    def setUp(self):
        organization = Organization.objects.create(
            name='Woningcorporatie',
            federation_type=FEDERATION_TYPE_WONINGCORPORATIE,
        )
        self.federation = Federation.objects.create(
            name='Woningcorporatie',
            federation_id='woningcorporatie',
            main_email='centraal@example.com',
            organization=organization,
        )
        self.case = Case.objects.create(
            woningcorporatie=self.federation,
            adres_stadsdeel='Centrum',
        )

    def test_all_addresses_for_case_district_are_returned(self):
        StadsdeelEmail.objects.create(
            federation=self.federation,
            stadsdeel='Centrum',
            email='centrum-a@example.com',
        )
        StadsdeelEmail.objects.create(
            federation=self.federation,
            stadsdeel='Centrum',
            email='centrum-b@example.com',
        )
        StadsdeelEmail.objects.create(
            federation=self.federation,
            stadsdeel='Noord',
            email='noord@example.com',
        )

        self.assertCountEqual(
            get_woningcorporatie_medewerkers_email_list(self.case),
            ['centrum-a@example.com', 'centrum-b@example.com'],
        )

    def test_central_addresses_are_used_when_district_has_no_match(self):
        self.assertEqual(
            get_woningcorporatie_medewerkers_email_list(self.case),
            ['centraal@example.com'],
        )

    def test_settings_form_prefills_existing_addresses(self):
        for email in ['centrum-a@example.com', 'centrum-b@example.com']:
            StadsdeelEmail.objects.create(
                federation=self.federation,
                stadsdeel='Centrum',
                email=email,
            )

        form = StadsdeelEmailForm(instance=self.federation)

        self.assertEqual(
            form['Centrum'].value(),
            'centrum-a@example.com, centrum-b@example.com',
        )
        self.assertEqual(form['Noord'].value(), '')

    def test_settings_form_supports_create_update_and_delete(self):
        form = StadsdeelEmailForm(
            data={
                'district_emails-Centrum': ' centrum-a@example.com, centrum-b@example.com ',
                'district_emails-Noord': 'noord@example.com',
            },
            instance=self.federation,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertCountEqual(
            self.federation.district_emails.values_list('stadsdeel', 'email'),
            [
                ('Centrum', 'centrum-a@example.com'),
                ('Centrum', 'centrum-b@example.com'),
                ('Noord', 'noord@example.com'),
            ],
        )

        form = StadsdeelEmailForm(
            data={
                'district_emails-Centrum': 'centrum-nieuw@example.com',
                'district_emails-Noord': '',
            },
            instance=self.federation,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.assertEqual(
            list(self.federation.district_emails.values_list('email', flat=True)),
            ['centrum-nieuw@example.com'],
        )

    def test_invalid_address_in_list_is_rejected(self):
        form = StadsdeelEmailForm(
            data={'district_emails-Centrum': 'valid@example.com, geen-e-mailadres'},
            instance=self.federation,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('Centrum', form.errors)
        with self.assertRaises(ValueError):
            form.save()
        self.assertFalse(self.federation.district_emails.exists())

    def login_federation_manager(self):
        user = User.objects.create(
            username='beheerder@example.com',
            user_type=[str(FEDERATIE_BEHEERDER)],
            federation=self.federation,
        )
        Profile.objects.create(user=user)
        self.client.force_login(user)

    def test_update_page_saves_district_addresses(self):
        self.login_federation_manager()

        response = self.client.post(
            reverse('federation_update', args=[self.federation.pk]),
            {
                'main_email': 'nieuw-centraal@example.com',
                'district_emails-Centrum': 'centrum-a@example.com, centrum-b@example.com',
            },
        )

        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)
        self.federation.refresh_from_db()
        self.assertEqual(self.federation.main_email, 'nieuw-centraal@example.com')
        self.assertCountEqual(
            get_woningcorporatie_medewerkers_email_list(self.case),
            ['centrum-a@example.com', 'centrum-b@example.com'],
        )
        self.assertEqual(self.federation.district_emails.count(), 2)
