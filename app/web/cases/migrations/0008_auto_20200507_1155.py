# Generated by Django 2.2.10 on 2020-05-07 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0007_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='datum_evaluatie_moment',
            field=models.DateField(blank=True, null=True, verbose_name='Datum evaluatie moment'),
        ),
        migrations.AddField(
            model_name='case',
            name='datum_voordracht',
            field=models.DateField(blank=True, null=True, verbose_name='Datum voordracht'),
        ),
        migrations.AddField(
            model_name='case',
            name='omklap_beoordeeld_door',
            field=models.TextField(blank=True, null=True, verbose_name='Dit is beoordeeld door'),
        ),
        migrations.AddField(
            model_name='case',
            name='omklap_client_openstaande_vragen',
            field=models.TextField(blank=True, null=True, verbose_name='Voor deze cliënt staan de volgende vragen nog open'),
        ),
        migrations.AddField(
            model_name='case',
            name='omklap_client_volgende_stappen_gezet',
            field=models.TextField(blank=True, null=True, verbose_name='Hiervoor worden de volgende stappen gezet (zowel formeel als informeel)'),
        ),
        migrations.AddField(
            model_name='case',
            name='omklap_datum_evaluatiemoment',
            field=models.DateField(blank=True, null=True, verbose_name='Datum evaluatiemoment'),
        ),
        migrations.AddField(
            model_name='case',
            name='organisatie',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Organisatie'),
        ),
        migrations.AddField(
            model_name='case',
            name='persoonlijk_begeleider',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Persoonlijk begeleider'),
        ),
        migrations.AddField(
            model_name='case',
            name='start_zelfstandig_wonen',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Start zelfstandig wonen (intermediair)'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_functioneert_psychisch_akkoord',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Ja'), (2, 'Nee')], null=True, verbose_name='Akkoord'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_functioneert_psychisch_behaald_omdat',
            field=models.TextField(blank=True, null=True, verbose_name='Deze doelen zijn behaald omdat'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_functioneert_psychisch_beoordeeld_door',
            field=models.TextField(blank=True, null=True, verbose_name='Deze doelen zijn beoordeeld door'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_functioneert_psychisch_datum_evaluatiemoment',
            field=models.DateField(blank=True, null=True, verbose_name='Datum evaluatiemoment'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_functioneert_sociaal_akkoord',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Ja'), (2, 'Nee')], null=True, verbose_name='Akkoord'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_functioneert_sociaal_behaald_omdat',
            field=models.TextField(blank=True, null=True, verbose_name='Deze doelen zijn behaald omdat'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_functioneert_sociaal_beoordeeld_door',
            field=models.TextField(blank=True, null=True, verbose_name='Deze doelen zijn beoordeeld door'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_functioneert_sociaal_datum_evaluatiemoment',
            field=models.DateField(blank=True, null=True, verbose_name='Datum evaluatiemoment'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_is_financieel_stabiel_akkoord',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Ja'), (2, 'Nee')], null=True, verbose_name='Akkoord'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_is_financieel_stabiel_behaald_omdat',
            field=models.TextField(blank=True, null=True, verbose_name='Deze doelen zijn behaald omdat'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_is_financieel_stabiel_beoordeeld_door',
            field=models.TextField(blank=True, null=True, verbose_name='Deze doelen zijn beoordeeld door'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_is_financieel_stabiel_datum_evaluatiemoment',
            field=models.DateField(blank=True, null=True, verbose_name='Datum evaluatiemoment'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_kinderen_gezonde_akkoord',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Ja'), (2, 'Nee')], null=True, verbose_name='Akkoord'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_kinderen_gezonde_behaald_omdat',
            field=models.TextField(blank=True, null=True, verbose_name='Deze doelen zijn behaald omdat'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_kinderen_gezonde_beoordeeld_door',
            field=models.TextField(blank=True, null=True, verbose_name='Deze doelen zijn beoordeeld door'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_kinderen_gezonde_datum_evaluatiemoment',
            field=models.DateField(blank=True, null=True, verbose_name='Datum evaluatiemoment'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_zinvolle_dagbesteding_akkoord',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Ja'), (2, 'Nee')], null=True, verbose_name='Akkoord'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_zinvolle_dagbesteding_behaald_omdat',
            field=models.TextField(blank=True, null=True, verbose_name='Deze doelen zijn behaald omdat'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_zinvolle_dagbesteding_beoordeeld_door',
            field=models.TextField(blank=True, null=True, verbose_name='Deze doelen zijn beoordeeld door'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_zinvolle_dagbesteding_datum_evaluatiemoment',
            field=models.DateField(blank=True, null=True, verbose_name='Datum evaluatiemoment'),
        ),
        migrations.AddField(
            model_name='case',
            name='woningcorporatie_akkoord_met_omklap',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Ja'), (2, 'Nee')], null=True, verbose_name='Woningcorporatie akkoord met omklap'),
        ),
    ]