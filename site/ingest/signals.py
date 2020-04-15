from django.db.models.signals import post_save

from django.dispatch import receiver

from ingest import models, apps


@receiver(post_save, sender=models.RawFile)
def compile_file(sender, instance, created, **kwargs):
    if instance.merged and not instance.is_parsed:
        apps.IngestConfig.dmodels.merge(
            created_by=instance.modify_by, raw_file=instance)
    if not instance.merged and instance.is_parsed:
        apps.IngestConfig.dmodels.remove(raw_file=instance)
