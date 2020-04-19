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


class RawFile(TimeStampedModel):

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.DO_NOTHING,
        related_name="%(class)s_createdby")
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.DO_NOTHING,
        related_name="%(class)s_modifiedby", null=True, blank=True
    )

    DATA_FILE_EXTENSIONS = [e[1:] for e in mdesc.DATA_FILE_EXTENSIONS]

    file = models.FileField(
        upload_to=_raw_file_upload_to,
        validators=[
            FileExtensionValidator(allowed_extensions=DATA_FILE_EXTENSIONS)],
        verbose_name="archivo")

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


# =============================================================================
# INGEST MODELS ABSTRACT
# =============================================================================

class BaseIngestModel(TimeStampedModel):
    principal = False
    identifier  = None

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.DO_NOTHING,
        related_name="%(class)s_createdby")
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.DO_NOTHING,
        related_name="%(class)s_modifiedby", null=True, blank=True
    )

    @classmethod
    def verbose_name_plural(cls):
        return cls._meta.verbose_name.title()

    @classmethod
    def model_name(cls):
        return cls.__name__

    @classmethod
    def get_fields(cls):
        return {
            f.name: f for f in cls._meta.get_fields()
            if not isinstance(f, (models.ManyToOneRel, models.ManyToManyRel))}

    class Meta:
        abstract = True


# =============================================================================
# CONCRETE  INGEST MODELS
# =============================================================================

class ClasificacionEpidemiologica(BaseIngestModel):
    nombre_ce = models.CharField(unique=True, max_length=255)

    identifier = "nombre_ce"


class Pais(BaseIngestModel):
    id_pais = models.IntegerField(unique=True)
    nombre_pais = models.CharField(max_length=255, blank=True, null=True)

    identifier = "id_pais"


class Provincia(BaseIngestModel):
    id_provincia = models.IntegerField(unique=True)
    nombre_provincia = models.CharField(max_length=255, blank=True, null=True)
    pais = models.ForeignKey(Pais, models.DO_NOTHING, blank=True, null=True)

    identifier = "id_provincia"


class Departamento(BaseIngestModel):
    id_departamento = models.IntegerField(unique=True)
    nombre_departamento = models.CharField(
        max_length=255, blank=True, null=True)
    provincia = models.ForeignKey(
        "Provincia", models.DO_NOTHING, blank=True, null=True)

    identifier = "id_departamento"


class Localidad(BaseIngestModel):
    id_localidad = models.IntegerField(unique=True)
    nombre_localidad = models.CharField(
        max_length=255, blank=True, null=True)
    departamento = models.ForeignKey(
        Departamento, models.DO_NOTHING, blank=True, null=True)

    identifier = "id_localidad"


class Paciente(BaseIngestModel):
    nombre_paciente = models.CharField(unique=True, max_length=255)
    sexo = models.CharField(max_length=2, blank=True, null=True)
    sepi_apertura = models.IntegerField(blank=True, null=True)
    edad_actual = models.IntegerField(blank=True, null=True)
    localidad_residencia = models.ForeignKey(
        Localidad, models.DO_NOTHING, blank=True, null=True)

    identifier = "nombre_paciente"


class Sintoma(BaseIngestModel):
    nombre_sintoma = models.CharField(unique=True, max_length=255)
    notas_sintoma = models.TextField(blank=True, null=True)

    identifier = "nombre_sintoma"


class TipoEvento(BaseIngestModel):
    nombre_tipo_evento = models.CharField(unique=True, max_length=255)
    notas_tipo_evento = models.TextField(blank=True, null=True)

    identifier = "nombre_tipo_evento"


class EventoSignoSintoma(TimeStampedModel):
    evento = models.ForeignKey("Evento", models.DO_NOTHING)
    sintoma = models.ForeignKey("Sintoma", models.DO_NOTHING)

    class Meta:
        db_table = "ingest_evento_signo_sintoma"
        unique_together = (("evento", "sintoma"),)


class Evento(BaseIngestModel):
    principal = True
    identifier = "id"

    paciente = models.ForeignKey(
        "Paciente", models.CASCADE,
        related_name="eventos", blank=True, null=True)
    fecha_internacion = models.DateField(blank=True, null=True)
    tipo_evento = models.ForeignKey(
        "TipoEvento", models.CASCADE, blank=True, null=True)
    notas_evento = models.TextField(blank=True, null=True)
    raw_file = models.ForeignKey(
        "RawFile", models.DO_NOTHING, related_name="generated")
    sintomas = models.ManyToManyField(
        "Sintoma", through=EventoSignoSintoma)
