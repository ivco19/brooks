#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Arcovid-19 Brooks.
# Copyright (c) 2020, Juan B Cabral, Vanessa Daza, Diego García Lambas,
#                     Marcelo Lares, Nadia Luczywo, Dante Paz, Rodrigo Quiroga,
#                     Bruno Sanchez, Federico Stasyszyn.
# License: BSD-3-Clause
#   Full Text: https://github.com/ivco19/brooks/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""Static models for the ingest app."""


# =============================================================================
# IMPORTS
# =============================================================================

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django_extensions.db.models import TimeStampedModel

from ingest.libs import mdesc


# =============================================================================
# RAW FILE UPLOAD
# =============================================================================


def _raw_file_upload_to(instance, filename):
    folder = instance.created.strftime("%Y_%m")
    return "/".join(["raw_files", folder, filename])


class Tracked(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, related_name="%(class)s_createdby")
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.DO_NOTHING, related_name="%(class)s_modifiedby", null=True, blank=True
    )

    class Meta:
        abstract = True


class RawFile(TimeStampedModel, Tracked):

    DATA_FILE_EXTENSIONS = [e[1:] for e in mdesc.DATA_FILE_EXTENSIONS]

    file = models.FileField(
        upload_to=_raw_file_upload_to,
        validators=[FileExtensionValidator(allowed_extensions=DATA_FILE_EXTENSIONS)],
        verbose_name="archivo",
    )

    notes = models.TextField(blank=True, verbose_name="notas")
    merged = models.BooleanField(default=False, verbose_name="integrado")
    size = models.IntegerField(null=True)

    broken = models.BooleanField(default=False, verbose_name="Roto")

    @property
    def is_parsed(self):
        return bool(self.generated.count())

    @property
    def filename(self):
        return self.file.url.rsplit("/", 1)[-1]


class ClasificacionEpidemiologica(TimeStampedModel, Tracked):
    nombre_ce = models.CharField(unique=True, max_length=255)

    class Meta:
        db_table = "ingest_clasificacionepidemiologica"


class Departamento(TimeStampedModel, Tracked):
    nombre_departamento = models.CharField(max_length=255, blank=True, null=True)
    provincia = models.ForeignKey("Provincia", models.DO_NOTHING, blank=True, null=True)


class Localidad(TimeStampedModel, Tracked):
    nombre_localidad = models.CharField(max_length=255, blank=True, null=True)
    departamento = models.ForeignKey(Departamento, models.DO_NOTHING, blank=True, null=True)


class Paciente(TimeStampedModel, Tracked):
    nombre_paciente = models.CharField(unique=True, max_length=255)
    sexo = models.CharField(max_length=2, blank=True, null=True)
    sepi_apertura = models.IntegerField(blank=True, null=True)
    edad_actual = models.IntegerField(blank=True, null=True)
    localidad_residencia = models.ForeignKey(Localidad, models.DO_NOTHING, blank=True, null=True)


class Pais(TimeStampedModel, Tracked):
    nombre_pais = models.CharField(max_length=255, blank=True, null=True)

class Provincia(TimeStampedModel, Tracked):
    nombre_provincia = models.CharField(max_length=255, blank=True, null=True)
    pais = models.ForeignKey(Pais, models.DO_NOTHING, blank=True, null=True)


class Sintoma(TimeStampedModel, Tracked):
    nombre_sintoma = models.CharField(unique=True, max_length=255)
    notas_sintoma = models.TextField(blank=True, null=True)


class TipoEvento(TimeStampedModel, Tracked):
    nombre_tipo_evento = models.CharField(unique=True, max_length=255)
    notas_tipo_evento = models.TextField(blank=True, null=True)


class EventoSignoSintoma(TimeStampedModel, Tracked):
    evento = models.ForeignKey("Evento", models.DO_NOTHING)
    sintoma = models.ForeignKey("Sintoma", models.DO_NOTHING)

    class Meta:
        db_table = "ingest_evento_signo_sintoma"
        unique_together = (("evento", "sintoma"),)


class Evento(TimeStampedModel, Tracked):
    fecha_internacion = models.DateField(blank=True, null=True)
    notas_evento = models.TextField(blank=True, null=True)
    paciente = models.ForeignKey("Paciente", related_name="eventos", models.DO_NOTHING, blank=True, null=True)
    raw_file = models.ForeignKey("RawFile", models.DO_NOTHING)
    tipo_evento = models.ForeignKey("Tipoevento", models.DO_NOTHING, blank=True, null=True)
