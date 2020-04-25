# Generated by Django 3.0.4 on 2020-04-19 21:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0003_auto_20200418_1629'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clasificacionepidemiologica',
            options={},
        ),
        migrations.AlterModelOptions(
            name='departamento',
            options={},
        ),
        migrations.AlterModelOptions(
            name='evento',
            options={},
        ),
        migrations.AlterModelOptions(
            name='localidad',
            options={},
        ),
        migrations.AlterModelOptions(
            name='paciente',
            options={},
        ),
        migrations.AlterModelOptions(
            name='pais',
            options={},
        ),
        migrations.AlterModelOptions(
            name='provincia',
            options={},
        ),
        migrations.AlterModelOptions(
            name='rawfile',
            options={},
        ),
        migrations.AlterModelOptions(
            name='sintoma',
            options={},
        ),
        migrations.AlterModelOptions(
            name='tipoevento',
            options={},
        ),
        migrations.AlterField(
            model_name='evento',
            name='raw_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='generated', to='ingest.RawFile'),
        ),
    ]