# Generated by Django 2.2.10 on 2020-03-27 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0003_auto_20200326_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='aanvraag_datum',
            field=models.DateField(blank=True, null=True, verbose_name='Datum aanvraag'),
        ),
        migrations.AddField(
            model_name='case',
            name='centrale_toegang_naam',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'CTBW'), (2, 'CTMO'), (3, 'CTMOJ'), (4, 'CTMOG'), (5, 'JEUGDHULP'), (6, 'CTBWLvB')], null=True, verbose_name='Naam centrale toegang'),
        ),
        migrations.AddField(
            model_name='case',
            name='centrale_toegang_trajectwijziging_ed',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'CTBW'), (2, 'CTMO'), (3, 'CTMOJ'), (4, 'CTMOG'), (5, 'JEUGDHULP'), (6, 'CTBWLvB')], null=True, verbose_name='Toegang en trajectwijziging / doorstroom en jeugdzorg'),
        ),
        migrations.AddField(
            model_name='case',
            name='jonger_dan_26',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Nee'), (2, 'Ja: standaard plaatsing jongerenwoning (5 jaar contract bij omklap)'), (3, 'Ja: plaatsing reguliere woning noodzakelijk (onbepaalde tijd bij omklap)'), (4, 'Ja: Plaatsing in een project: ……………………………')], null=True, verbose_name='Plaatsing jonger dan 26 jaar'),
        ),
        migrations.AddField(
            model_name='case',
            name='jonger_dan_26_motivatie_contract_onbepaalde',
            field=models.TextField(blank=True, null=True, verbose_name='Motivatie voor contract onbepaalde tijd jongere'),
        ),
        migrations.AddField(
            model_name='case',
            name='jonger_dan_26_plaatsing_project',
            field=models.TextField(blank=True, null=True, verbose_name='Plaatsing jonger project'),
        ),
        migrations.AddField(
            model_name='case',
            name='medische_problemen_bewijslast',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Voeg medische gegevens toe m.b.t. problematiek'),
        ),
        migrations.AddField(
            model_name='case',
            name='medische_problemen_mbt_traplopen',
            field=models.BooleanField(blank=True, null=True, verbose_name='Zijn er medische problemen m.b.t. traplopen?'),
        ),
        migrations.AddField(
            model_name='case',
            name='medische_problemen_wooneisen',
            field=models.TextField(blank=True, null=True, verbose_name='Zo ja, benedenwoning of woning met lift? Anders?'),
        ),
        migrations.AddField(
            model_name='case',
            name='omslagwoning_zorgaanbieder',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Zorgaanbieder omslagwoning'),
        ),
        migrations.AddField(
            model_name='case',
            name='partner_echtscheiding_rond',
            field=models.BooleanField(blank=True, null=True, verbose_name='Echtscheiding rond?'),
        ),
        migrations.AddField(
            model_name='case',
            name='partner_geboortedatum',
            field=models.DateField(blank=True, null=True, verbose_name='Partner geboortedatum'),
        ),
        migrations.AddField(
            model_name='case',
            name='partner_gehuwd',
            field=models.BooleanField(blank=True, null=True, verbose_name='Gehuwd?'),
        ),
        migrations.AddField(
            model_name='case',
            name='partner_naam',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Partner naam'),
        ),
        migrations.AddField(
            model_name='case',
            name='partner_woonsituatie',
            field=models.TextField(blank=True, null=True, verbose_name='Woonsituatie partner'),
        ),
        migrations.AddField(
            model_name='case',
            name='trajecthouder_naam',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Naam instroomfunctionaris of trajecthouder'),
        ),
        migrations.AddField(
            model_name='case',
            name='uitsluiting_stadsdeel_argumentatie',
            field=models.TextField(blank=True, null=True, verbose_name='Uitsluiting stadsdeel, argumentatie'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_functioneert_psychisch_stabiel',
            field=models.TextField(blank=True, null=True, verbose_name='De cliënt functioneert psychisch stabiel'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_functioneert_sociaal_stabiel',
            field=models.TextField(blank=True, null=True, verbose_name='De cliënt functioneert sociaal stabiel'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_is_financieel_stabiel',
            field=models.TextField(blank=True, null=True, verbose_name='De cliënt is financieel stabiel'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_kinderen_gezonde_omgeving',
            field=models.TextField(blank=True, null=True, verbose_name='De betrokken kinderen hebben een gezonde omgeving'),
        ),
        migrations.AddField(
            model_name='case',
            name='urgentiecriteria_zinvolle_dagbesteding',
            field=models.TextField(blank=True, null=True, verbose_name='De cliënt heeft passende zinvolle dagbesteding'),
        ),
        migrations.AddField(
            model_name='case',
            name='woningnet_geldigheid',
            field=models.DateField(blank=True, null=True, verbose_name='Geldigheid woninget'),
        ),
        migrations.AddField(
            model_name='case',
            name='woningnet_nummer',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Woningnetnummer'),
        ),
    ]