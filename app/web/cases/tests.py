from datetime import timedelta
from unittest.mock import patch

from django.contrib.sessions.models import Session
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from web.cases.forms import CaseAddressForm, CaseAddressUpdateForm
from web.cases.models import Case, CaseStatus
from web.organizations.models import Federation, Organization
from web.organizations.statics import (
    FEDERATION_TYPE_ADW,
    FEDERATION_TYPE_WONINGCORPORATIE,
    FEDERATION_TYPE_ZORGINSTELLING,
)
from web.profiles.models import Profile
from web.users.models import User
from web.users.statics import BEGELEIDER, WONEN


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


@override_settings(EMAIL_HOST_USER='local')
class CaseMailFlowTestCase(TestCase):
    def setUp(self):
        self.wonen_federation = Federation.objects.create(
            name='Wonen',
            federation_id='wonen',
            organization=Organization.objects.create(
                name='Wonen', federation_type=FEDERATION_TYPE_ADW
            ),
            main_email='wonen@example.com',
        )
        self.federation = Federation.objects.create(
            name='Zorginstelling',
            federation_id='zorginstelling',
            organization=Organization.objects.create(
                name='Zorginstelling', federation_type=FEDERATION_TYPE_ZORGINSTELLING
            ),
            main_email='controle@example.com',
        )
        self.user = self.create_user('begeleider@example.com', BEGELEIDER, self.federation)
        self.colleague = self.create_user('collega@example.com', BEGELEIDER, self.federation)
        self.wonen_user = self.create_user('wonen@example.com', WONEN, self.wonen_federation)
        self.case = Case.objects.create(
            adres_straatnaam='Amstel',
            adres_huisnummer='1',
            adres_postcode='1011PN',
            adres_plaatsnaam='Amsterdam',
        )
        for user in (self.user, self.colleague):
            user.profile.cases.add(self.case)
        self.client.force_login(self.user)

    def create_user(self, username, user_type, federation):
        user = User.objects.create(
            username=username, user_type=[str(user_type)], federation=federation
        )
        Profile.objects.get_or_create(user=user)
        return user

    def assert_mail(self, subject, link_text=None):
        message = mail.outbox[-1]
        html = message.alternatives[0][0]
        self.assertEqual(message.subject, subject)
        self.assertIn('Gemeente Amsterdam', html)
        if link_text:
            self.assertIn('%s:' % link_text, html)
            self.assertIn('https://', message.body)
        else:
            self.assertNotIn('https://', message.body)

    def test_case_deleted(self):
        self.client.force_login(self.wonen_user)

        self.client.post(reverse('delete_case', kwargs={'pk': self.case.id}))

        self.assert_mail('Omslagroute - Cliënt definitief verwijderd')
        self.assertIn('begeleider@example.com', mail.outbox[-1].to)

    def test_delete_request(self):
        self.client.post(
            reverse('delete_request_case', kwargs={'pk': self.case.id}),
            {'delete_request_message': 'Reden'},
        )

        self.assert_mail('Omslagroute - Verzoek verwijderen cliënt', 'Cliëntgegevens bekijken')
        self.assertIn('Reden', mail.outbox[-1].body)

    def test_delete_request_revoke(self):
        Case.objects.filter(pk=self.case.pk).update(delete_request_date=timezone.now())

        self.client.post(
            reverse('delete_request_revoke_case', kwargs={'pk': self.case.id}),
            {'delete_request_revoke_message': 'Toch niet'},
        )

        self.assert_mail(
            'Omslagroute - Verzoek verwijderen cliënt teruggedraaid', 'Cliëntgegevens bekijken'
        )
        self.assertIn('Toch niet', mail.outbox[-1].body)

    def test_validate_case(self):
        self.client.get(
            reverse(
                'validate_case',
                kwargs={'pk': self.case.id, 'form_config_slug': 'aanvraag-omklap'},
            )
        )

        self.assert_mail('Omslagroute - Aanvraag Voordracht omklap controleren', 'Formulier bekijken')

    def test_send_case(self):
        self.client.post(
            reverse(
                'send_case',
                kwargs={'pk': self.case.id, 'form_config_slug': 'aanvraag-omklap'},
            ),
            {},
        )

        self.assert_mail('Omslagroute - Aanvraag Voordracht omklap ingediend', 'Formulier bekijken')

    def test_status_change(self):
        self.client.force_login(self.wonen_user)
        CaseStatus.objects.create(
            case=self.case, form='aanvraag-omklap', profile=self.user.profile, status=1
        )

        self.client.post(
            '/api/casestatus/',
            {'case': self.case.id, 'form': 'aanvraag-omklap', 'status': 2},
            content_type='application/json',
        )

        self.assertIn('Aanvraag Voordracht omklap, status:', mail.outbox[-1].subject)
        self.assertIn('Formulier bekijken:', mail.outbox[-1].alternatives[0][0])

    def test_remove_invited_user_has_no_link(self):
        self.client.post(
            reverse('case_remove_invited_users', kwargs={'pk': self.case.id}),
            {'user_list': [self.colleague.id]},
        )

        self.assert_mail('Omslagroute - je bent uit een team verwijderd')
        self.assertEqual(mail.outbox[-1].to, ['collega@example.com'])

    @patch('web.cases.forms.get_stadsdeel', return_value='Centrum')
    def test_address_changed(self, _):
        woningcorporatie = Federation.objects.create(
            name='Woningcorporatie',
            federation_id='woningcorporatie',
            organization=Organization.objects.create(
                name='Woningcorporatie', federation_type=FEDERATION_TYPE_WONINGCORPORATIE
            ),
        )

        self.client.post(
            reverse('update_case_address', kwargs={'pk': self.case.id}),
            {
                'adres_straatnaam': 'Dam',
                'adres_huisnummer': '1',
                'adres_postcode': '1012JS',
                'adres_plaatsnaam': 'Amsterdam',
                'nummeraanduiding_id': '1',
                'woningcorporatie': woningcorporatie.id,
                'wijziging_reden': 'Verhuisd',
            },
        )

        self.assert_mail('Omslagroute - Adres van cliënt gewijzigd', 'Cliëntgegevens bekijken')

    def test_invite(self):
        url = reverse('case_invite_users', kwargs={'pk': self.case.id})
        invited = self.create_user('uitgenodigd@example.com', BEGELEIDER, self.federation)
        self.client.post(
            url,
            {'case_invite_users-current_step': '0', '0-user_list': [invited.id]},
        )

        self.client.post(
            url,
            {'case_invite_users-current_step': '1', '1-message': "Kijk je mee?"},
        )

        self.assert_mail('Omslagroute - je bent toegevoegd aan een team', 'Cliënt bekijken')
        self.assertEqual(mail.outbox[-1].to, ['uitgenodigd@example.com'])
        self.assertIn('Kijk je mee?', mail.outbox[-1].body)
