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

"""Static tables for the ingest app."""


# =============================================================================
# IMPORTS
# =============================================================================

import os

from django_tables2 import Table, Column

from django.urls import reverse

from ingest import models


# =============================================================================
# CONSTANTS
# =============================================================================

CONFIRMED_CLASSES = {
    True: "table-success confirmed",
    False: "table-danger no-confirmed d-none"}


# =============================================================================
# TABLES
# =============================================================================

class RawFileTable(Table):
    open = Column(
        accessor="pk", verbose_name="Abrir",
        linkify=lambda record: reverse('ingest:check_file', args=[record.pk]))
    created = Column(verbose_name="Fecha de creación")
    modified = Column(verbose_name="Última modificación")
    file = Column()
    size = Column(verbose_name="Registros")
    rcreated = Column(verbose_name="Registros generados")

    class Meta:
        model = models.RawFile
        exclude = ["notes"]
        attrs = {
            "class": "table table-hover",
            "thead": {"class": "thead-dark"}}
        row_attrs = {
            "class": lambda record: CONFIRMED_CLASSES[record.merged]}
        sequence = ('id', 'created_by', "...", "open")

    def render_open(self, value):
        return f"Ver #{value}"

    def render_created_by(self, value):
        if value.last_name and value.first_name:
            return f"{value.last_name}, {value.first_name} (@{value.username})"
        return f"@{value.username}"

    def render_file(self, value):
        return os.path.basename(value.file.name)

    def render_rcreated(self, value):
        return value.count()

    def render_size(self, value, record):
        try:
            return record.size
        except Exception:
            return "Incorrecto"
