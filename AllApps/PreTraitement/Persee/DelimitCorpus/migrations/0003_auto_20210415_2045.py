# Generated by Django 2.1.7 on 2021-04-15 20:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DelimitCorpus', '0002_auto_20210415_1928'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transformer',
            name='DocTransformeRef',
        ),
        migrations.AddField(
            model_name='transformer',
            name='DocExtractRef',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.DocExtractInitial'),
            preserve_default=False,
        ),
    ]