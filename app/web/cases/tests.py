from datetime import timedelta
from unittest.mock import patch

from django.contrib.sessions.models import Session
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from web.cases.forms import CaseAddressForm, CaseAddressUpdateForm
from web.cases.models import Case
from web.organizations.models import Federation, Organization
from web.organizations.statics import (
    FEDERATION_TYPE_WONINGCORPORATIE,
    FEDERATION_TYPE_ZORGINSTELLING,
)
from web.profiles.models import Profile
from web.users.models import User
from web.users.statics import BEGELEIDER


class AddressStadsdeelTestCase(TestCase):
    def setUp(self):
        organization = Organization.objects.create(
            name='Woningcorporatie',
            federation_type=FEDERATION_TYPE_WONINGCORPORATIE,
        )
        self.federation = Federation.objects.create(
            name='Woningcorporatie',
            federation_id='woningcorporatie',
            organization=organization,
        )
        self.case = Case.objects.create(
            adres_straatnaam='Amstel',
            adres_huisnummer='1',
            adres_postcode='1011PN',
            adres_plaatsnaam='Amsterdam',
            adres_stadsdeel='Centrum',
            woningcorporatie=self.federation,
        )

    def get_data(self, **kwargs):
        data = {
            'adres_straatnaam': 'Amstel',
            'adres_huisnummer': '1',
            'adres_postcode': '1011PN',
            'adres_plaatsnaam': 'Amsterdam',
            'woningcorporatie': self.federation.id,
            'wijziging_reden': 'Verhuisd',
        }
        data.update(kwargs)
        return data

    @patch('web.cases.forms.get_stadsdeel', return_value='Noord')
    def test_stadsdeel_is_updated_when_address_changes(self, mock_get_stadsdeel):
        form = CaseAddressUpdateForm(
            data=self.get_data(adres_straatnaam='Buikslotermeerplein', nummeraanduiding_id='0363200000000001'),
            instance=self.case,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.case.refresh_from_db()
        self.assertEqual(self.case.adres_stadsdeel, 'Noord')
        mock_get_stadsdeel.assert_called_once_with('0363200000000001')

    @patch('web.cases.forms.get_stadsdeel')
    def test_stadsdeel_is_kept_when_address_is_unchanged(self, mock_get_stadsdeel):
        form = CaseAddressUpdateForm(data=self.get_data(), instance=self.case)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        self.case.refresh_from_db()
        self.assertEqual(self.case.adres_stadsdeel, 'Centrum')
        mock_get_stadsdeel.assert_not_called()

    @patch('web.cases.forms.get_stadsdeel')
    def test_changed_address_without_selected_suggestion_is_invalid(self, mock_get_stadsdeel):
        form = CaseAddressUpdateForm(
            data=self.get_data(adres_straatnaam='Buikslotermeerplein'),
            instance=self.case,
        )
        self.assertFalse(form.is_valid())
        self.assertTrue(form.non_field_errors())
        mock_get_stadsdeel.assert_not_called()

    @patch('web.cases.forms.get_stadsdeel', return_value=None)
    def test_unknown_stadsdeel_is_invalid(self, mock_get_stadsdeel):
        form = CaseAddressUpdateForm(
            data=self.get_data(adres_straatnaam='Buikslotermeerplein', nummeraanduiding_id='0363200000000001'),
            instance=self.case,
        )
        self.assertFalse(form.is_valid())
        self.assertTrue(form.non_field_errors())

        self.case.refresh_from_db()
        self.assertEqual(self.case.adres_stadsdeel, 'Centrum')

    @patch('web.cases.forms.get_stadsdeel')
    def test_invalid_nummeraanduiding_id_is_rejected(self, mock_get_stadsdeel):
        form = CaseAddressUpdateForm(
            data=self.get_data(adres_straatnaam='Buikslotermeerplein', nummeraanduiding_id='../123'),
            instance=self.case,
        )
        self.assertFalse(form.is_valid())
        mock_get_stadsdeel.assert_not_called()

    @patch('web.cases.forms.get_stadsdeel', return_value='Zuidoost')
    def test_stadsdeel_is_set_for_new_address(self, mock_get_stadsdeel):
        case = Case.objects.create()
        form = CaseAddressForm(
            data=self.get_data(nummeraanduiding_id='0363200000000001'),
            instance=case,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()

        case.refresh_from_db()
        self.assertEqual(case.adres_stadsdeel, 'Zuidoost')

    @patch('web.cases.forms.get_stadsdeel')
    def test_new_address_without_selected_suggestion_is_invalid(self, mock_get_stadsdeel):
        case = Case.objects.create()
        form = CaseAddressForm(data=self.get_data(), instance=case)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.non_field_errors())


class CaseFormSaveTestCase(TestCase):
    def setUp(self):
        organization = Organization.objects.create(
            name='Zorginstelling',
            federation_type=FEDERATION_TYPE_ZORGINSTELLING,
        )
        federation = Federation.objects.create(
            name='Zorginstelling',
            federation_id='zorginstelling',
            organization=organization,
        )
        user = User.objects.create(
            username='begeleider@example.com',
            user_type=[str(BEGELEIDER)],
            federation=federation,
        )
        profile, _ = Profile.objects.get_or_create(user=user)
        self.case = Case.objects.create(
            adres_straatnaam='Amstel',
            adres_huisnummer='1',
            adres_postcode='1011PN',
            adres_plaatsnaam='Amsterdam',
        )
        profile.cases.add(self.case)
        self.client.force_login(user)
        self.url = reverse(
            'update_case',
            kwargs={'pk': self.case.id, 'form_config_slug': 'aanvraag-omklap'},
        )

    def test_save_without_phone_number_keeps_the_text(self):
        response = self.client.post(self.url, {'omklap_toelichting': 'tekst'})

        self.assertEqual(response.status_code, 302)
        self.case.refresh_from_db()
        self.assertEqual(self.case.omklap_toelichting, 'tekst')

    def test_empty_phone_number_still_blocks_submitting(self):
        response = self.client.post(
            self.url, {'omklap_toelichting': 'tekst', 'next': '/verstuur/'}
        )

        self.assertEqual(response['Location'], '%s?control=1' % self.url)

    def test_invalid_phone_number_is_still_rejected(self):
        response = self.client.post(
            self.url,
            {
                'omklap_toelichting': 'tekst',
                'persoonlijk_begeleider_telefoonnummer': 'onbekend',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.case.refresh_from_db()
        self.assertIsNone(self.case.omklap_toelichting)

    def test_rejected_save_shows_error_instead_of_queued_saved_message(self):
        self.client.post(self.url, {'omklap_toelichting': 'eerste'})

        response = self.client.post(
            self.url, {'datum_voordracht': 'geen datum'}
        )

        self.assertContains(response, 'Niet opgeslagen: 1 veld is niet goed ingevuld.')
        self.assertNotContains(response, 'Eventuele wijzigingen zijn opgeslagen.')

    def test_rejected_save_counts_invalid_fields(self):
        response = self.client.post(
            self.url,
            {
                'datum_voordracht': 'geen datum',
                'persoonlijk_begeleider_telefoonnummer': 'onbekend',
            },
        )

        self.assertContains(response, 'Niet opgeslagen: 2 velden zijn niet goed ingevuld.')

    def test_saved_message_is_shown_after_valid_save(self):
        response = self.client.post(
            self.url, {'omklap_toelichting': 'tekst'}, follow=True
        )

        self.assertContains(response, 'Eventuele wijzigingen zijn opgeslagen.')
        self.assertNotContains(response, 'Niet opgeslagen')


class SessionKeepAliveTestCase(TestCase):
    def setUp(self):
        self.url = reverse('session_keep_alive')

    def test_returns_csrf_token_when_logged_in(self):
        self.client.force_login(User.objects.create(username='a@example.com'))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['csrf_token'])

    def test_extends_the_session(self):
        self.client.force_login(User.objects.create(username='a@example.com'))
        key = self.client.session.session_key
        Session.objects.filter(session_key=key).update(
            expire_date=timezone.now() + timedelta(minutes=1)
        )

        self.client.get(self.url)

        expire_date = Session.objects.get(session_key=key).expire_date
        self.assertGreater(expire_date, timezone.now() + timedelta(minutes=50))

    def test_returns_login_url_when_session_expired(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)
        self.assertIn('login_url', response.json())

    def test_login_url_returns_to_the_form(self):
        response = self.client.get(self.url, {'next': '/clienten/1/aanvraag-omklap/'})

        self.assertIn(
            'next=/clienten/1/aanvraag-omklap/', response.json()['login_url']
        )
