import shutil
import os
import django.apps

from django.conf import settings

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Clean the database and remove all the uploaded files"

    def handle(self, *args, **options):
        if not settings.DEMO_MODE:
            raise CommandError("This command can only run in DEMO_MODE")

        print(f"!!! Reset DB")
        for model in django.apps.apps.get_models():
            model.objects.all().delete()

        print(f"!!! Removing {settings.MEDIA_ROOT}")
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)
