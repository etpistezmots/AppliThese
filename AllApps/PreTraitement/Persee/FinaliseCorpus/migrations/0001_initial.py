# Generated by Django 2.1.7 on 2021-04-15 18:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('DelimitCorpus', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CorpusAdd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150, unique=True)),
                ('user_restrict', models.CharField(max_length=150)),
                ('date', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='CorpusComplet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150, unique=True)),
                ('user_restrict', models.CharField(max_length=150)),
                ('date', models.CharField(max_length=80)),
                ('EltRemove', models.TextField()),
                ('CorpusAddRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FinaliseCorpus.CorpusAdd')),
                ('CorpusEtudeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DelimitCorpus.CorpusEtude')),
            ],
        ),
        migrations.CreateModel(
            name='CorpusFin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150, unique=True)),
                ('user_restrict', models.CharField(max_length=150)),
                ('date', models.CharField(max_length=80)),
                ('PretraitIraBase', models.BooleanField()),
                ('Lemmatisation', models.BooleanField()),
                ('CorpusCompletRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FinaliseCorpus.CorpusComplet')),
            ],
        ),
        migrations.CreateModel(
            name='DicoExpression',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150, unique=True)),
                ('user_restrict', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='DicoMotLemme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150, unique=True)),
                ('user_restrict', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='DicoSuffixe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150, unique=True)),
                ('user_restrict', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='FNRRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CorpusCompletRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FinaliseCorpus.CorpusComplet')),
                ('DicoExpressionRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FinaliseCorpus.DicoExpression')),
                ('DicoMotLemmeRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FinaliseCorpus.DicoMotLemme')),
            ],
        ),
        migrations.CreateModel(
            name='TextAdd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=550)),
                ('nomfichier', models.CharField(max_length=150)),
                ('annee', models.IntegerField()),
                ('type', models.CharField(max_length=80)),
                ('revue', models.CharField(max_length=50)),
                ('auteurs', models.CharField(max_length=550)),
                ('CorpusAddRef', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FinaliseCorpus.CorpusAdd')),
            ],
        ),
        migrations.AddField(
            model_name='corpusfin',
            name='DicoExpressionRef',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FinaliseCorpus.DicoExpression'),
        ),
        migrations.AddField(
            model_name='corpusfin',
            name='DicoMotLemmeRef',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FinaliseCorpus.DicoMotLemme'),
        ),
        migrations.AddField(
            model_name='corpusfin',
            name='DicoSuffixeRef',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FinaliseCorpus.DicoSuffixe'),
        ),
    ]
