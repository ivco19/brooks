# Generated by Django 3.0.4 on 2020-04-19 22:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0004_auto_20200419_2127'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rawfile',
            options={'get_latest_by': 'modified', 'ordering': ('-modified', '-created')},
        ),
    ]