
import os

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import FileExtensionValidator

from django_extensions.db.models import TimeStampedModel

import pandas as pd

import pandas_interactive_html

pandas_interactive_html.register()


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
        validators=[FileExtensionValidator(allowed_extensions=EXTENSIONS)],
        verbose_name="archivo")
    notes = models.TextField(blank=True, verbose_name="notas")
    confirmed = models.BooleanField(default=False, verbose_name="confirmado")

    created_by = models.ForeignKey(
        User, related_name="raw_files",
        on_delete=models.CASCADE, verbose_name="creado por")

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

# =============================================================================
# REAL MODELS
# =============================================================================

class Patient(TimeStampedModel):

    patient_raw_file_id = models.IntegerField(
        unique=True, verbose_name="ID de archivo")
    gender = models.CharField(max_length=255, verbose_name="género")
    nationality = models.CharField(max_length=255, verbose_name="nacionalidad")
    address = models.CharField(max_length=255, verbose_name="dirección")
    notes = models.TextField(blank=True, verbose_name="notas", null=True)


class Sintoms(TimeStampedModel):

        description = models.CharField(
            max_length=255, verbose_name="description")


class InfectionSource(TimeStampedModel):

    desc = models.CharField(max_length=255, verbose_name="Description")


class Event(TimeStampedModel):

    STATUSES = {
        "suspected": "Sospechoso",
        "active": "Activo",
        "recovered": "Recuperado",
        "deceased": "Fallecido"}

    raw_file = models.ForeignKey(
        RawFile, related_name="events",
        on_delete=models.CASCADE, verbose_name="Archivo")

    sintoms = models.ManyToManyField(Sintoms, related_name="events")

    event_raw_file_id = models.IntegerField(unique=True)
    patient = models.ForeignKey(
        Patient, related_name="events",
        on_delete=models.CASCADE, verbose_name="Paciente")

    status = models.CharField(
        max_length=50, choices=list(STATUSES.items()))

    lock_address = models.CharField(max_length=255)

    has_simptoms = models.BooleanField(null=True)
    first_simptoms_date = models.DateField(null=True)
    confirmed_date = models.DateField(null=True)
    deceased_date = models.DateField(null=True)
    discharge_date = models.DateField(null=True)
