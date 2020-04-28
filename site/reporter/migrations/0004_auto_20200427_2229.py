# Generated by Django 3.0.4 on 2020-04-27 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporter', '0003_reportconfiguration_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportconfiguration',
            name='body',
            field=models.TextField(default='\n<h1>Informe diario {{now}}</h1>\n\n{% for m in models %}\n{{m}}\n{% endfor %}\n', verbose_name='Cuerpo'),
        ),
        migrations.AlterField(
            model_name='reportconfiguration',
            name='footer',
            field=models.TextField(default='\n<hr>\n<p>Generated with Brooks <code>{{now}}</code></p>\n<p><a href="http://ivco19.github.io/">http://ivco19.github.io/</a></p>\n', verbose_name='pie'),
        ),
        migrations.AlterField(
            model_name='reportconfiguration',
            name='header',
            field=models.TextField(default='', verbose_name='encabezado'),
        ),
    ]