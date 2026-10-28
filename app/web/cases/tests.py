from unittest.mock import patch

from django.test import TestCase

from web.cases.forms import CaseAddressForm, CaseAddressUpdateForm
from web.cases.models import Case
from web.organizations.models import Federation, Organization
from web.organizations.statics import FEDERATION_TYPE_WONINGCORPORATIE


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
