
import os

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import FileExtensionValidator

from django_extensions.db.models import TimeStampedModel

import pandas as pd


# =============================================================================
# RAW FILE UPLOAD
# =============================================================================

def _raw_file_upload_to(instance, filename):
    folder = instance.created.strftime("%Y_%m")
    return '/'.join(["raw_files", folder, filename])


class RawFile(TimeStampedModel):
    PARSERS = {
        "csv": pd.read_csv,
        "xlsx": pd.read_excel,
    }
    EXTENSIONS = list(PARSERS)

    file = models.FileField(
        upload_to=_raw_file_upload_to,
        validators=[FileExtensionValidator(allowed_extensions=EXTENSIONS)])
    notes = models.TextField(blank=True)
    confirmed = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        User, related_name="raw_files",
        on_delete=models.CASCADE, verbose_name="Created by")

    @property
    def filename(self):
        return self.file.url.rsplit("/", 1)[-1]

    @property
    def ext(self):
        return os.path.splitext(self.filename)[-1]

    def as_df(self):
        parser = self.PARSERS[self.ext[1:]]
        df = parser(self.file.path)
        return df