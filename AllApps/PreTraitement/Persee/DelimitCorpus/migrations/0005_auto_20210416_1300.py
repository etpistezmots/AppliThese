# Generated by Django 2.1.7 on 2021-04-16 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DelimitCorpus', '0004_auto_20210416_0943'),
    ]

    operations = [
        migrations.AddField(
            model_name='synthesetransform',
            name='SupprAnnCombiTextualBasdePage',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='synthesetransform',
            name='SupprEspSup1990BasdePage',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
