# Generated by Django 2.2.10 on 2020-05-14 08:46

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0010_auto_20200512_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='forms',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[['aanvraag-omslag-en-urgentie', 'Aanvraag omslag en urgentie'], ['aanvraag-omklap', 'Aanvraag omklap']], max_length=43, null=True, verbose_name='Formulieren'),
        ),
    ]