# Generated by Django 2.1.7 on 2021-04-15 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('TableauEmb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FastTextRCluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomresult', models.CharField(max_length=200, unique=True)),
                ('user_restrict2', models.CharField(max_length=100)),
                ('choixrevue', models.CharField(max_length=100)),
                ('choixepoque', models.CharField(max_length=100)),
                ('terme', models.CharField(max_length=100)),
                ('nresult', models.PositiveIntegerField()),
                ('methode_clustering', models.CharField(choices=[('Kmeans', 'Kmeans'), ('AggloMoyenne', 'AggloMoyenne'), ('AggloMin', 'AggloMin'), ('AggloMax', 'AggloMax')], default=None, max_length=100)),
                ('ncluster', models.PositiveIntegerField()),
                ('link', models.BooleanField()),
                ('color_singleton', models.BooleanField()),
                ('modelc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TableauEmb.FastText')),
            ],
        ),
        migrations.CreateModel(
            name='GloveRCluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomresult', models.CharField(max_length=200, unique=True)),
                ('user_restrict2', models.CharField(max_length=100)),
                ('choixrevue', models.CharField(max_length=100)),
                ('choixepoque', models.CharField(max_length=100)),
                ('terme', models.CharField(max_length=100)),
                ('nresult', models.PositiveIntegerField()),
                ('methode_clustering', models.CharField(choices=[('Kmeans', 'Kmeans'), ('AggloMoyenne', 'AggloMoyenne'), ('AggloMin', 'AggloMin'), ('AggloMax', 'AggloMax')], default=None, max_length=100)),
                ('ncluster', models.PositiveIntegerField()),
                ('link', models.BooleanField()),
                ('color_singleton', models.BooleanField()),
                ('modelc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TableauEmb.Glove')),
            ],
        ),
        migrations.CreateModel(
            name='Word2VecRCluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomresult', models.CharField(max_length=200, unique=True)),
                ('user_restrict2', models.CharField(max_length=100)),
                ('choixrevue', models.CharField(max_length=100)),
                ('choixepoque', models.CharField(max_length=100)),
                ('terme', models.CharField(max_length=100)),
                ('nresult', models.PositiveIntegerField()),
                ('methode_clustering', models.CharField(choices=[('Kmeans', 'Kmeans'), ('AggloMoyenne', 'AggloMoyenne'), ('AggloMin', 'AggloMin'), ('AggloMax', 'AggloMax')], default=None, max_length=100)),
                ('ncluster', models.PositiveIntegerField()),
                ('link', models.BooleanField()),
                ('color_singleton', models.BooleanField()),
                ('modelc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TableauEmb.Word2Vec')),
            ],
        ),
    ]
