# Generated by Django 2.2.9 on 2020-02-26 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0010_auto_20200221_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentversion',
            name='uploaded_file',
            field=models.FileField(upload_to='uploads', verbose_name='Selecteer een bestand'),
        ),
    ]