# Generated by Django 2.2.10 on 2020-03-19 08:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='case',
            options={'ordering': ('client_last_name',), 'verbose_name': 'Client', 'verbose_name_plural': 'Clienten'},
        ),
    ]