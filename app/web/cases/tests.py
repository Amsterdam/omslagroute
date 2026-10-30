from datetime import timedelta
from unittest.mock import patch

from django.contrib.sessions.models import Session
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from web.cases.forms import CaseAddressForm, CaseAddressUpdateForm
from web.cases.models import Case, CaseStatus
from web.cases.statics import (
    CASE_STATUS_GOEDGEKEURD,
    CASE_STATUS_INGEDIEND,
    CASE_STATUS_WONINGCORPORATIE_GOEDGEKEURD,
)
from web.organizations.models import Federation, Organization
from web.organizations.statics import (
    FEDERATION_TYPE_ADW,
    FEDERATION_TYPE_WONINGCORPORATIE,
    FEDERATION_TYPE_ZORGINSTELLING,
)
from web.profiles.models import Profile
from web.users.models import User
from web.users.statics import BEGELEIDER, WONEN, WONINGCORPORATIE_MEDEWERKER


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
        self.case.create_version('aanvraag-omklap')
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


@override_settings(EMAIL_HOST_USER='local')
class CaseInviteAccessTestCase(TestCase):
    def setUp(self):
        organization = Organization.objects.create(
            name='Zorginstelling', federation_type=FEDERATION_TYPE_ZORGINSTELLING
        )
        federation = Federation.objects.create(
            name='Zorginstelling', federation_id='zorginstelling', organization=organization
        )
        other_federation = Federation.objects.create(
            name='Andere zorginstelling',
            federation_id='andere-zorginstelling',
            organization=Organization.objects.create(
                name='Andere zorginstelling', federation_type=FEDERATION_TYPE_ZORGINSTELLING
            ),
        )
        self.user = self.create_user('begeleider@example.com', federation)
        self.colleague = self.create_user('collega@example.com', federation)
        self.other_user = self.create_user('ander@example.com', other_federation)
        self.own_case = Case.objects.create()
        self.foreign_case = Case.objects.create()
        self.user.profile.cases.add(self.own_case)
        self.other_user.profile.cases.add(self.foreign_case)
        self.client.force_login(self.user)

    def create_user(self, username, federation):
        user = User.objects.create(
            username=username,
            email=username,
            user_type=[str(BEGELEIDER)],
            federation=federation,
        )
        Profile.objects.get_or_create(user=user)
        return user

    def invite_colleague(self, case):
        url = reverse('case_invite_users', kwargs={'pk': case.id})
        self.client.post(
            url, {'case_invite_users-current_step': '0', '0-user_list': [self.colleague.id]}
        )
        return self.client.post(
            url, {'case_invite_users-current_step': '1', '1-message': ''}
        )

    def invite_other_organization(self, case):
        url = reverse('case_invite_users_federation', kwargs={'pk': case.id})
        self.client.post(
            url,
            {
                'case_invite_users_cross_federation-current_step': '0',
                '0-user_email_cross_federation': 'ander@example.com',
            },
        )
        return self.client.post(
            url, {'case_invite_users_cross_federation-current_step': '1', '1-message': ''}
        )

    def test_invite_on_own_case(self):
        self.invite_colleague(self.own_case)

        self.assertTrue(self.colleague.profile.cases.filter(id=self.own_case.id).exists())

    def test_invite_other_organization_on_own_case(self):
        self.invite_other_organization(self.own_case)

        self.assertTrue(self.other_user.profile.cases.filter(id=self.own_case.id).exists())

    def test_invite_on_case_of_colleague(self):
        self.colleague.profile.cases.add(self.foreign_case)
        third = self.create_user('derde@example.com', self.user.federation)
        url = reverse('case_invite_users', kwargs={'pk': self.foreign_case.id})

        self.client.post(
            url, {'case_invite_users-current_step': '0', '0-user_list': [third.id]}
        )
        self.client.post(url, {'case_invite_users-current_step': '1', '1-message': ''})

        self.assertTrue(third.profile.cases.filter(id=self.foreign_case.id).exists())

    def test_invite_other_organization_on_case_of_colleague(self):
        self.colleague.profile.cases.add(self.own_case)
        self.user.profile.cases.remove(self.own_case)

        self.invite_other_organization(self.own_case)

        self.assertTrue(self.other_user.profile.cases.filter(id=self.own_case.id).exists())

    def test_invite_on_foreign_case_is_denied(self):
        response = self.invite_colleague(self.foreign_case)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.colleague.profile.cases.filter(id=self.foreign_case.id).exists())

    def test_invite_other_organization_on_foreign_case_is_denied(self):
        self.other_user.profile.cases.remove(self.foreign_case)

        response = self.invite_other_organization(self.foreign_case)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.other_user.profile.cases.filter(id=self.foreign_case.id).exists())

    def test_invite_pages_of_foreign_case_are_denied(self):
        for name in ('case_invite_users', 'case_invite_users_federation'):
            response = self.client.get(reverse(name, kwargs={'pk': self.foreign_case.id}))

            self.assertEqual(response.status_code, 403)


class CaseStatusApiTestCase(TestCase):
    url = '/api/casestatus/'

    def setUp(self):
        self.wonen_federation = self.create_federation('wonen', FEDERATION_TYPE_ADW)
        self.corporation = self.create_federation('corporatie', FEDERATION_TYPE_WONINGCORPORATIE)
        other_corporation = self.create_federation(
            'andere-corporatie', FEDERATION_TYPE_WONINGCORPORATIE
        )
        self.wonen_user = self.create_user('wonen@example.com', WONEN, self.wonen_federation)
        self.corporation_user = self.create_user(
            'corporatie@example.com', WONINGCORPORATIE_MEDEWERKER, self.corporation
        )
        self.begeleider = self.create_user('begeleider@example.com', BEGELEIDER, self.corporation)
        self.case = Case.objects.create(woningcorporatie=self.corporation)
        self.foreign_case = Case.objects.create(woningcorporatie=other_corporation)
        for case in (self.case, self.foreign_case):
            case.create_version('aanvraag-omklap')
            case.create_version('evaluatie-wonen')

    def create_federation(self, name, federation_type):
        return Federation.objects.create(
            name=name,
            federation_id=name,
            organization=Organization.objects.create(name=name, federation_type=federation_type),
        )

    def create_user(self, username, user_type, federation):
        user = User.objects.create(
            username=username, user_type=[str(user_type)], federation=federation
        )
        Profile.objects.get_or_create(user=user)
        return user

    def post(self, user, **data):
        self.client.force_login(user)
        return self.client.post(self.url, data, content_type='application/json')

    def corporation_status(self, **data):
        status_data = {
            'case': self.case.id,
            'form': 'evaluatie-wonen',
            'status': CASE_STATUS_WONINGCORPORATIE_GOEDGEKEURD,
        }
        status_data.update(data)
        return self.post(self.corporation_user, **status_data)

    def test_status_is_saved_on_own_case(self):
        response = self.post(
            self.wonen_user, case=self.case.id, form='aanvraag-omklap', status=CASE_STATUS_GOEDGEKEURD
        )

        self.assertEqual(response.status_code, 201)
        status = CaseStatus.objects.get(case=self.case)
        self.assertEqual(status.profile, self.wonen_user.profile)
        self.assertIsNotNone(status.case_version)

    def test_status_on_foreign_case_is_denied(self):
        response = self.corporation_status(case=self.foreign_case.id)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(CaseStatus.objects.exists())

    def test_profile_from_request_is_ignored(self):
        response = self.corporation_status(profile=self.begeleider.profile.id)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(CaseStatus.objects.get().profile, self.corporation_user.profile)

    def test_case_version_from_request_is_ignored(self):
        version = self.foreign_case.create_version('evaluatie-wonen')

        self.corporation_status(status=CASE_STATUS_INGEDIEND, case_version=version.id)

        self.assertIsNone(CaseStatus.objects.get().case_version)

    def test_form_of_other_organization_type_is_denied(self):
        response = self.corporation_status(form='aanvraag-omklap')

        self.assertEqual(response.status_code, 403)
        self.assertFalse(CaseStatus.objects.exists())

    def test_status_of_other_organization_type_is_denied(self):
        response = self.corporation_status(status=CASE_STATUS_GOEDGEKEURD)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(CaseStatus.objects.exists())

    def test_history_is_readable(self):
        self.corporation_status()

        response = self.client.get(self.url, {'case': self.case.id, 'form': 'evaluatie-wonen'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_history_cannot_be_changed_or_deleted(self):
        self.corporation_status()
        url = '%s%s/' % (self.url, CaseStatus.objects.get().id)

        for method in (self.client.put, self.client.patch, self.client.delete):
            response = method(url, {}, content_type='application/json')

            self.assertEqual(response.status_code, 405)
        self.assertTrue(CaseStatus.objects.exists())
