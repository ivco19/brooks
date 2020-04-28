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

import os
import itertools as it

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django_extensions.db.models import TimeStampedModel

from brooks.libs.dmatplotlib import MatplotlibManager

from django_pandas.managers import DataFrameManager

import pandas as pd


# =============================================================================
# RAW FILE UPLOAD
# =============================================================================

def _raw_file_upload_to(instance, filename):
    folder = instance.created.strftime("%Y_%m")
    return "/".join(["raw_files", folder, filename])


class RawFile(TimeStampedModel):

    DATA_FILE_PARSERS = {
        ".csv": pd.read_csv,
        ".xlsx": pd.read_excel,
    }

    DATA_FILE_EXTENSIONS = [e[1:] for e in DATA_FILE_PARSERS]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.DO_NOTHING,
        related_name="%(class)s_createdby")
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.DO_NOTHING,
        related_name="%(class)s_modifiedby", null=True, blank=True
    )

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

    def as_df(self):
        ext = os.path.splitext(self.filename)[-1]
        parser = self.DATA_FILE_PARSERS[ext]
        return parser(self.file.path)


# =============================================================================
# INGEST MODELS ABSTRACT
# =============================================================================

class IngestPlotManager(MatplotlibManager):

    draw_methods = ["plot_creation_time"]

    def _sin_datos(self, fig, ax):
        ax.text(
            0.6, 0.7, "Datos", size=50, rotation=30., ha="center", va="center",
            bbox={
                "boxstyle": "round",
                "ec": (1., 0.5, 0.5),
                "fc": (1., 0.8, 0.8)})
        ax.text(
            0.5, 0.5, "Sin", size=50, rotation=-25., ha="right", va="top",
            bbox={
                "boxstyle": "round",
                "ec": (1., 0.5, 0.5),
                "fc": (1., 0.8, 0.8)})

        ax.set_yticks([])
        ax.set_xticks([])

    def plot_creation_time(self, fig, ax, **kwargs):
        queryset = self.get_queryset()
        dmodel_name = self.model.verbose_name_plural()

        ax.set_title(f"{dmodel_name} creados y modificados por fecha")
        ax.set_ylabel(f"Número de {dmodel_name}")
        ax.set_xlabel("Fecha")

        if not queryset.exists():
            self._sin_datos(fig, ax)
            return

        datac, datam = {}, {}
        for instance in queryset:
            created = instance.created.date()
            datac[created] = datac.setdefault(created, 0) + 1

            modified = instance.modified.date()
            datam[modified] = datam.setdefault(modified, 0) + 1

        for idx in range(10):
            import datetime as dt
            import random
            now = (dt.datetime.now() + dt.timedelta(days=idx)).date()
            datac[now] = random.randint(1, 100)
            datam[now] = random.randint(1, 100)

        ax.plot(
            [k.isoformat() for k in datac.keys()],
            list(datac.values()), ls="--", marker="o", label="Creados")

        ax.plot(
            [k.isoformat() for k in datam.keys()],
            list(datam.values()), ls="--", marker="o", label="Modificados")

        xtick_labels = [l for l in sorted(it.chain(datac, datam))]
        ax.set_xticklabels(xtick_labels, rotation=45)

        ax.legend()


class BaseIngestModel(TimeStampedModel):
    principal = False
    identifier  = None

    objects = DataFrameManager()
    plots = IngestPlotManager()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.DO_NOTHING,
        related_name="%(class)s_createdby")
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.DO_NOTHING,
        related_name="%(class)s_modifiedby", null=True, blank=True
    )

    @classmethod
    def get_identifier(self):
        return "id" if self.principal else self.identifier

    @classmethod
    def model_resume(cls):
        return getattr(
            cls, "resume",
            f"No hay nada para decir sobre {cls.model_name()}")

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

    @classmethod
    def get_plot_methods(cls):
        draw_methods = self.draw_methods or ["draw_plot"]
        methods = [getattr(self, m) for m in draw_methods]
        return methods

    def __str__(self):
        idf = self.get_identifier()
        idfv = getattr(self, idf)
        return f"{self.model_name()}({idf}={idfv})"

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
    evento = models.ForeignKey("Evento", models.CASCADE)
    sintoma = models.ForeignKey("Sintoma", models.DO_NOTHING)

    class Meta:
        db_table = "ingest_evento_signo_sintoma"
        unique_together = (("evento", "sintoma"),)


class Evento(BaseIngestModel):
    principal = True

    paciente = models.ForeignKey(
        "Paciente", models.CASCADE,
        related_name="eventos", blank=True, null=True)
    fecha_internacion = models.DateField(blank=True, null=True)
    tipo_evento = models.ForeignKey(
        "TipoEvento", models.CASCADE, blank=True, null=True)
    sintomas = models.ManyToManyField(
        "Sintoma", through=EventoSignoSintoma)

    notas_evento = models.TextField(blank=True, null=True)

    raw_file = models.ForeignKey(
        "RawFile", models.DO_NOTHING, related_name="generated")
