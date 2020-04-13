
import os
import json

import dateutil

from django.db import models, transaction
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import FileExtensionValidator

from django_extensions.db.models import TimeStampedModel

import numpy as np

import pandas as pd

import pandas_interactive_html


from libs import model_descriptions as mdesc


# =============================================================================
# RAW FILE UPLOAD
# =============================================================================

def _raw_file_upload_to(instance, filename):
    folder = instance.created.strftime("%Y_%m")
    return '/'.join(["raw_files", folder, filename])


class RawFile(TimeStampedModel):

    DATA_FILE_EXTENSIONS = [e[1:] for e in mdesc.DATA_FILE_EXTENSIONS]

    file = models.FileField(
        upload_to=_raw_file_upload_to,
        validators=[
            FileExtensionValidator(allowed_extensions=DATA_FILE_EXTENSIONS)],
        verbose_name="archivo")

    notes = models.TextField(blank=True, verbose_name="notas")
    merged = models.BooleanField(default=False, verbose_name="integrado")

    created_by = models.ForeignKey(
        User, related_name="raw_files",
        on_delete=models.CASCADE, verbose_name="creado por")

    @property
    def filename(self):
        return self.file.url.rsplit("/", 1)[-1]


    # def remove_events(self, commit=False):
    #     if commit and not self.is_parsed:
    #         raise ValueError(f"RawFile #{self.pk} no esta cargado")
    #     with transaction.atomic():
    #         self.events.all().delete()
    #         if commit:
    #             self.is_parsed = False
    #         else:
    #             transaction.set_rollback(True)





