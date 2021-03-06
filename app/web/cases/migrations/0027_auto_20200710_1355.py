# Generated by Django 2.2.10 on 2020-07-10 13:55

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0026_auto_20200710_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='aanvraag_omklap_actief',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Aanvraag omklap actief'),
        ),
        migrations.AddField(
            model_name='case',
            name='aanvraag_omklap_alle_doelen_behaald',
            field=models.TextField(blank=True, null=True, verbose_name='Aanvraag omklap alle doelen behaald'),
        ),
        migrations.AddField(
            model_name='case',
            name='aanvraag_omklap_steunstructuren',
            field=models.TextField(blank=True, null=True, verbose_name='Aanvraag omklap steunstructuren'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_afval',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie afval'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_akkoord_bewoner',
            field=models.BooleanField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie akkoord bewoner'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_akkoord_bewoner_datum',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie akkoord bewoner datum'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_akkoord_bewoner_naam',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie akkoord bewoner naam'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_akkoord_zorgaanbieder',
            field=models.BooleanField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie akkoord zorgaanbieder'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_akkoord_zorgaanbieder_datum',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie akkoord zorgaanbieder datum'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_akkoord_zorgaanbieder_naam',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie akkoord zorgaanbieder naam'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_borg_bedrag',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie borg bedrag'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_borg_betalen',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie borg betalen'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_doelen_wonen_huurderschap',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie doelen wonen huurderschap'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_goed_huurderschap',
            field=models.BooleanField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie goed huurderschap'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_goede_buur',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie goede buur'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_huisregels',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie huisregels'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_kennisgemaakt_buren',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie kennisgemaakt buren'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_kennismaken_buren',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie kennismaken buren'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_ondersteuning_medewerker',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie ondersteuning medewerker'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_overlast_melden',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie overlast melden'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_overlast_signalen',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie overlast signalen'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_overlast_voorkomen',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie overlast voorkomen'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_technische_klachten',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie technische klachten'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_wijk',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie wijk'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_wijk_voorzieningen_anders',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie wijk voorzieningen anders'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_wijk_voorzieningen_behoefte',
            field=models.TextField(blank=True, null=True, verbose_name='kennismaking_wooncorporatie_wijk_voorzieningen behoefte'),
        ),
        migrations.AddField(
            model_name='case',
            name='kennismaking_wooncorporatie_wijk_voorzieningen_waar',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie_wijk voorzieningen waar'),
        ),
        migrations.AddField(
            model_name='case',
            name='woningcorporatie_datum_kennismakingsgesprek',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Woningcorporatie datum kennismakingsgesprek'),
        ),
        migrations.AddField(
            model_name='case',
            name='woningcorporatie_datum_woonevaluatiegesprek',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Woningcorporatie datum woonevaluatiegesprek'),
        ),
        migrations.AddField(
            model_name='case',
            name='woningcorporatie_start_intermediaire_verhuur',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Woningcorporatie start intermediaire verhuur'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_akkoord_bewoner',
            field=models.BooleanField(blank=True, null=True, verbose_name='Woonevaluatie akkoord bewoner'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_akkoord_bewoner_datum',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Woonevaluatie akkoord bewoner datum'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_akkoord_bewoner_naam',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie akkoord bewoner naam'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_akkoord_zorgaanbieder',
            field=models.BooleanField(blank=True, null=True, verbose_name='Woonevaluatie akkoord zorgaanbieder'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_akkoord_zorgaanbieder_datum',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Woonevaluatie akkoord zorgaanbieder datum'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_akkoord_zorgaanbieder_naam',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie akkoord zorgaanbieder naam'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_bijzonderheden_wonen',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie bijzonderheden wonen'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_contact_met_buren',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie contact met buren'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_contact_met_buren_gewenst',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie contact met buren gewenst'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_contact_met_buren_verloop',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie contact met buren verloop'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_ervaring_wonen',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie ervaring wonen'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_goed_minder_goed',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie goed minder goed'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_huur_betalen_op_tijd',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie huur betalen op tijd'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_huur_betalen_regeling',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie huur betalen regeling'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_moment_volgend_gesprek',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie moment volgend gesprek'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_netwerk_aanwezig',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie netwerk aanwezig'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_netwerk_behoefte',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie netwerk behoefte'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_netwerk_behoefte_meer_contacten',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie netwerk behoefte meer contacten'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_netwerk_hoe_gaat_dat',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie netwerk hoe gaat dat'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_omschrijving_balkon_tuin',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie omschrijving balkon tuin'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_omschrijving_portiek',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie omschrijving portiek'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_omschrijving_woning',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie omschrijving woning'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_overlast_buren',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie overlast buren'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_overlast_buren_gemeld',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie overlast buren gemeld'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_overlast_omwonenden_gemeld',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie overlast omwonenden gemeld'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_overlast_omwonenden_oplossing',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie overlast omwonenden oplossing'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='aanvraag_omklap_actief',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Aanvraag omklap actief'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='aanvraag_omklap_alle_doelen_behaald',
            field=models.TextField(blank=True, null=True, verbose_name='Aanvraag omklap alle doelen behaald'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='aanvraag_omklap_steunstructuren',
            field=models.TextField(blank=True, null=True, verbose_name='Aanvraag omklap steunstructuren'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_afval',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie afval'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_akkoord_bewoner',
            field=models.BooleanField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie akkoord bewoner'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_akkoord_bewoner_datum',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie akkoord bewoner datum'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_akkoord_bewoner_naam',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie akkoord bewoner naam'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_akkoord_zorgaanbieder',
            field=models.BooleanField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie akkoord zorgaanbieder'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_akkoord_zorgaanbieder_datum',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie akkoord zorgaanbieder datum'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_akkoord_zorgaanbieder_naam',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie akkoord zorgaanbieder naam'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_borg_bedrag',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie borg bedrag'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_borg_betalen',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie borg betalen'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_doelen_wonen_huurderschap',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie doelen wonen huurderschap'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_goed_huurderschap',
            field=models.BooleanField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie goed huurderschap'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_goede_buur',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie goede buur'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_huisregels',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie huisregels'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_kennisgemaakt_buren',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie kennisgemaakt buren'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_kennismaken_buren',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie kennismaken buren'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_ondersteuning_medewerker',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie ondersteuning medewerker'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_overlast_melden',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie overlast melden'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_overlast_signalen',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie overlast signalen'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_overlast_voorkomen',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie overlast voorkomen'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_technische_klachten',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie technische klachten'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_wijk',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie wijk'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_wijk_voorzieningen_anders',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie wijk voorzieningen anders'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_wijk_voorzieningen_behoefte',
            field=models.TextField(blank=True, null=True, verbose_name='kennismaking_wooncorporatie_wijk_voorzieningen behoefte'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='kennismaking_wooncorporatie_wijk_voorzieningen_waar',
            field=models.TextField(blank=True, null=True, verbose_name='Kennismaking wooncorporatie_wijk voorzieningen waar'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woningcorporatie_datum_kennismakingsgesprek',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Woningcorporatie datum kennismakingsgesprek'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woningcorporatie_datum_woonevaluatiegesprek',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Woningcorporatie datum woonevaluatiegesprek'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woningcorporatie_start_intermediaire_verhuur',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Woningcorporatie start intermediaire verhuur'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_akkoord_bewoner',
            field=models.BooleanField(blank=True, null=True, verbose_name='Woonevaluatie akkoord bewoner'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_akkoord_bewoner_datum',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Woonevaluatie akkoord bewoner datum'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_akkoord_bewoner_naam',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie akkoord bewoner naam'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_akkoord_zorgaanbieder',
            field=models.BooleanField(blank=True, null=True, verbose_name='Woonevaluatie akkoord zorgaanbieder'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_akkoord_zorgaanbieder_datum',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Woonevaluatie akkoord zorgaanbieder datum'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_akkoord_zorgaanbieder_naam',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie akkoord zorgaanbieder naam'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_bijzonderheden_wonen',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie bijzonderheden wonen'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_contact_met_buren',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie contact met buren'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_contact_met_buren_gewenst',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie contact met buren gewenst'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_contact_met_buren_verloop',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie contact met buren verloop'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_ervaring_wonen',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie ervaring wonen'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_goed_minder_goed',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie goed minder goed'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_huur_betalen_op_tijd',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie huur betalen op tijd'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_huur_betalen_regeling',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie huur betalen regeling'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_moment_volgend_gesprek',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie moment volgend gesprek'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_netwerk_aanwezig',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie netwerk aanwezig'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_netwerk_behoefte',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie netwerk behoefte'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_netwerk_behoefte_meer_contacten',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie netwerk behoefte meer contacten'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_netwerk_hoe_gaat_dat',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie netwerk hoe gaat dat'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_omschrijving_balkon_tuin',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie omschrijving balkon tuin'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_omschrijving_portiek',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie omschrijving portiek'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_omschrijving_woning',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie omschrijving woning'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_overlast_buren',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie overlast buren'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_overlast_buren_gemeld',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie overlast buren gemeld'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_overlast_omwonenden_gemeld',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Woonevaluatie overlast omwonenden gemeld'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_overlast_omwonenden_oplossing',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie overlast omwonenden oplossing'),
        ),
        migrations.AlterField(
            model_name='document',
            name='forms',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[['aanvraag-omslag-en-urgentie', 'Aanvraag Urgentie onder voorwaarden'], ['aanvraag-omklap', 'Aanvraag Voordracht omklap'], ['evaluatie-wonen', 'Evaluatie wonen'], ['kennismaking-woningcorporatie', 'Kennismaking woningcorporatie']], max_length=89, null=True, verbose_name='Formulieren'),
        ),
    ]
