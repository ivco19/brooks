# Generated by Django 3.0.5 on 2020-04-18 16:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ingest', '0002_auto_20200418_1328'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clasificacionepidemiologica',
            options={'get_latest_by': 'modified', 'ordering': ('-modified', '-created')},
        ),
        migrations.AlterModelOptions(
            name='departamento',
            options={'get_latest_by': 'modified', 'ordering': ('-modified', '-created')},
        ),
        migrations.AlterModelOptions(
            name='evento',
            options={'get_latest_by': 'modified', 'ordering': ('-modified', '-created')},
        ),
        migrations.AlterModelOptions(
            name='localidad',
            options={'get_latest_by': 'modified', 'ordering': ('-modified', '-created')},
        ),
        migrations.AlterModelOptions(
            name='paciente',
            options={'get_latest_by': 'modified', 'ordering': ('-modified', '-created')},
        ),
        migrations.AlterModelOptions(
            name='pais',
            options={'get_latest_by': 'modified', 'ordering': ('-modified', '-created')},
        ),
        migrations.AlterModelOptions(
            name='provincia',
            options={'get_latest_by': 'modified', 'ordering': ('-modified', '-created')},
        ),
        migrations.AlterModelOptions(
            name='sintoma',
            options={'get_latest_by': 'modified', 'ordering': ('-modified', '-created')},
        ),
        migrations.AlterModelOptions(
            name='tipoevento',
            options={'get_latest_by': 'modified', 'ordering': ('-modified', '-created')},
        ),
        migrations.RemoveField(
            model_name='evento',
            name='signo_sintoma',
        ),
        migrations.RemoveField(
            model_name='rawfile',
            name='modify_by',
        ),
        migrations.AddField(
            model_name='rawfile',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='rawfile_modifiedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='clasificacionepidemiologica',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='clasificacionepidemiologica_createdby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='clasificacionepidemiologica',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='clasificacionepidemiologica_modifiedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='departamento',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='departamento_createdby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='departamento',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='departamento_modifiedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='departamento',
            name='nombre_departamento',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='departamento',
            name='provincia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ingest.Provincia'),
        ),
        migrations.AlterField(
            model_name='evento',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='evento_createdby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='evento',
            name='fecha_internacion',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='evento',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='evento_modifiedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='evento',
            name='notas_evento',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='evento',
            name='paciente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='eventos', to='ingest.Paciente'),
        ),
        migrations.AlterField(
            model_name='evento',
            name='raw_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ingest.RawFile'),
        ),
        migrations.AlterField(
            model_name='evento',
            name='tipo_evento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ingest.TipoEvento'),
        ),
        migrations.AlterField(
            model_name='localidad',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='localidad_createdby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='localidad',
            name='departamento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ingest.Departamento'),
        ),
        migrations.AlterField(
            model_name='localidad',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='localidad_modifiedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='localidad',
            name='nombre_localidad',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='paciente_createdby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='edad_actual',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='localidad_residencia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ingest.Localidad'),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='paciente_modifiedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='sepi_apertura',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='sexo',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='pais',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='pais_createdby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pais',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='pais_modifiedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pais',
            name='nombre_pais',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='provincia',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='provincia_createdby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='provincia',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='provincia_modifiedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='provincia',
            name='nombre_provincia',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='provincia',
            name='pais',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ingest.Pais'),
        ),
        migrations.AlterField(
            model_name='rawfile',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='rawfile_createdby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sintoma',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sintoma_createdby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sintoma',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='sintoma_modifiedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sintoma',
            name='notas_sintoma',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tipoevento',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='tipoevento_createdby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tipoevento',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='tipoevento_modifiedby', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tipoevento',
            name='notas_tipo_evento',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='EventoSignoSintoma',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='eventosignosintoma_createdby', to=settings.AUTH_USER_MODEL)),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ingest.Evento')),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='eventosignosintoma_modifiedby', to=settings.AUTH_USER_MODEL)),
                ('sintoma', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ingest.Sintoma')),
            ],
            options={
                'db_table': 'ingest_evento_signo_sintoma',
                'unique_together': {('evento', 'sintoma')},
            },
        ),
        migrations.AddField(
            model_name='evento',
            name='sintomas',
            field=models.ManyToManyField(through='ingest.EventoSignoSintoma', to='ingest.Sintoma'),
        ),
    ]