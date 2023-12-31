# Generated by Django 2.1.7 on 2021-04-15 18:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('DelimitCorpus', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllExceptAdd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=80)),
                ('IndexDeb', models.IntegerField()),
                ('IndexFin', models.IntegerField()),
                ('TextField', models.TextField()),
                ('comment', models.CharField(max_length=250)),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
                ('DocTransformeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.DocTransforme')),
            ],
        ),
        migrations.CreateModel(
            name='AllExceptRemove',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=80)),
                ('IndexDeb', models.IntegerField()),
                ('IndexFin', models.IntegerField()),
                ('TextField', models.TextField()),
                ('comment', models.CharField(max_length=250)),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
                ('DocTransformeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.DocTransforme')),
            ],
        ),
        migrations.CreateModel(
            name='AppendixTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('suppr', models.BooleanField()),
                ('mots', models.TextField(max_length=400)),
                ('zone', models.PositiveIntegerField()),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='BasDePageTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('SupprAnnCombiTextual', models.BooleanField()),
                ('SupprEspSup1990', models.BooleanField()),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='BiblioTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('SupprBilioEtFin', models.BooleanField()),
                ('mots', models.TextField(max_length=400)),
                ('zone', models.PositiveIntegerField()),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='CedilleTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('litigecedille', models.BooleanField()),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='DocRemove',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=80)),
                ('comment', models.CharField(max_length=250)),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
                ('DocTransformeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.DocTransforme')),
            ],
        ),
        migrations.CreateModel(
            name='FigureTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('EssaiHomogeneTitre', models.BooleanField()),
                ('mots', models.TextField(max_length=600)),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='FinDocTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('ContenuCentreRemove', models.BooleanField()),
                ('mots', models.TextField(max_length=600)),
                ('ManuscritRemove', models.BooleanField()),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='FinLigneTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('normalise', models.BooleanField()),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='FinMotTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='HtDePageTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('seuilgeo', models.PositiveIntegerField()),
                ('seuilspgeo', models.PositiveIntegerField()),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='MotCleTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('mots', models.TextField(max_length=400)),
                ('zone', models.PositiveIntegerField()),
                ('AjoutMotCleFr', models.BooleanField()),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='NoteTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('SupprNoteBio', models.BooleanField()),
                ('SupprNoteEdito', models.BooleanField()),
                ('SupprNoteBasDePage', models.BooleanField()),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='ResumeTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('mots', models.TextField(max_length=400)),
                ('zone', models.PositiveIntegerField()),
                ('AjoutResumeFr', models.BooleanField()),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='SousTitreTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('remplace', models.BooleanField()),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='TitreTransform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=15)),
                ('seuil', models.FloatField()),
                ('SupprSlashSecondPart', models.BooleanField()),
                ('SupprBeforeTitre', models.BooleanField()),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
    ]
