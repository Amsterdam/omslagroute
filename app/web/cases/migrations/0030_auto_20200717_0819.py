# Generated by Django 2.2.10 on 2020-07-17 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0029_auto_20200710_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_gepersonaliseerd_doel_1',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 1'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_gepersonaliseerd_doel_1_behaald',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Ja'), (2, 'Nee')], null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 1 behaald'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_gepersonaliseerd_doel_1_stand_van_zaken',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 1,  stand van zaken'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_gepersonaliseerd_doel_2',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 2'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_gepersonaliseerd_doel_2_behaald',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Ja'), (2, 'Nee')], null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 2 behaald'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_gepersonaliseerd_doel_2_stand_van_zaken',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 2,  stand van zaken'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_gepersonaliseerd_doel_3',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 3'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_gepersonaliseerd_doel_3_behaald',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Ja'), (2, 'Nee')], null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 3 behaald'),
        ),
        migrations.AddField(
            model_name='case',
            name='woonevaluatie_gepersonaliseerd_doel_3_stand_van_zaken',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 3,  stand van zaken'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_gepersonaliseerd_doel_1',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 1'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_gepersonaliseerd_doel_1_behaald',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Ja'), (2, 'Nee')], null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 1 behaald'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_gepersonaliseerd_doel_1_stand_van_zaken',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 1,  stand van zaken'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_gepersonaliseerd_doel_2',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 2'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_gepersonaliseerd_doel_2_behaald',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Ja'), (2, 'Nee')], null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 2 behaald'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_gepersonaliseerd_doel_2_stand_van_zaken',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 2,  stand van zaken'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_gepersonaliseerd_doel_3',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 3'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_gepersonaliseerd_doel_3_behaald',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Ja'), (2, 'Nee')], null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 3 behaald'),
        ),
        migrations.AddField(
            model_name='caseversion',
            name='woonevaluatie_gepersonaliseerd_doel_3_stand_van_zaken',
            field=models.TextField(blank=True, null=True, verbose_name='Woonevaluatie gepersonaliseerd doel 3,  stand van zaken'),
        ),
        migrations.AlterField(
            model_name='case',
            name='woonevaluatie_akkoord_zorgaanbieder_naam',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie akkoord zorgaanbieder naam en functie'),
        ),
        migrations.AlterField(
            model_name='caseversion',
            name='woonevaluatie_akkoord_zorgaanbieder_naam',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Woonevaluatie akkoord zorgaanbieder naam en functie'),
        ),
    ]