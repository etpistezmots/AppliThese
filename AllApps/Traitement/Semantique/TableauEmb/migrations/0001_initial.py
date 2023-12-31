# Generated by Django 2.1.7 on 2021-04-15 18:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('FinaliseCorpus', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200, unique=True)),
                ('user_restrict', models.CharField(max_length=100)),
                ('revue', models.CharField(choices=[('Annales,Espace', 'Annales,Espace'), ('Annales', 'Annales'), ('Espace', 'Espace')], default=None, max_length=200)),
                ('epoque', models.CharField(max_length=300)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='FastTextR',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_restrict2', models.CharField(max_length=100)),
                ('nomresult', models.CharField(max_length=200, unique=True)),
                ('terme', models.CharField(max_length=100)),
                ('nresult', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='GloveR',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_restrict2', models.CharField(max_length=100)),
                ('nomresult', models.CharField(max_length=200, unique=True)),
                ('terme', models.CharField(max_length=100)),
                ('nresult', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Word2VecR',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_restrict2', models.CharField(max_length=100)),
                ('nomresult', models.CharField(max_length=200, unique=True)),
                ('terme', models.CharField(max_length=100)),
                ('nresult', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='FastText',
            fields=[
                ('expe_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='TableauEmb.Expe')),
                ('architecture', models.CharField(choices=[('cbow', 'cbow'), ('skipgram', 'skipgram')], default=None, max_length=20)),
                ('embedding_size', models.PositiveIntegerField()),
                ('context_size', models.PositiveIntegerField()),
                ('min_occurrences', models.PositiveIntegerField()),
                ('num_epochs', models.IntegerField()),
                ('min_n', models.PositiveIntegerField()),
                ('max_n', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('TableauEmb.expe',),
        ),
        migrations.CreateModel(
            name='Glove',
            fields=[
                ('expe_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='TableauEmb.Expe')),
                ('embedding_size', models.IntegerField()),
                ('context_size', models.IntegerField()),
                ('min_occurrences', models.IntegerField()),
                ('num_epochs', models.IntegerField()),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('TableauEmb.expe',),
        ),
        migrations.CreateModel(
            name='Word2Vec',
            fields=[
                ('expe_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='TableauEmb.Expe')),
                ('architecture', models.CharField(choices=[('cbow', 'cbow'), ('skipgram', 'skipgram')], default=None, max_length=20)),
                ('embedding_size', models.PositiveIntegerField()),
                ('context_size', models.PositiveIntegerField()),
                ('min_occurrences', models.PositiveIntegerField()),
                ('num_epochs', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('TableauEmb.expe',),
        ),
        migrations.AddField(
            model_name='expe',
            name='CorpusFinRef',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FinaliseCorpus.CorpusFin'),
        ),
        migrations.AddField(
            model_name='expe',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_tableauemb.expe_set+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='word2vecr',
            name='modelc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TableauEmb.Word2Vec'),
        ),
        migrations.AddField(
            model_name='glover',
            name='modelc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TableauEmb.Glove'),
        ),
        migrations.AddField(
            model_name='fasttextr',
            name='modelc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TableauEmb.FastText'),
        ),
    ]
