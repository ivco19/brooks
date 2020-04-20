from django.db import models
from django.db.models.signals import post_save

from django.dispatch import receiver

from ingest import models


@receiver(post_save, sender=models.RawFile)
def compile_file(sender, instance, created, **kwargs):
    if instance.confirmed and not instance.is_parsed:
        instance.parse(commit=True)
        instance.save()
    if not instance.confirmed and instance.is_parsed:
        instance.remove_events(commit=True)
        instance.save()