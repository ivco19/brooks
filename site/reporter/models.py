#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Arcovid-19 Brooks.
# Copyright (c) 2020, Juan B Cabral, Vanessa Daza, Diego García Lambas,
#                     Marcelo Lares, Nadia Luczywo, Dante Paz, Rodrigo Quiroga,
#                     Bruno Sanchez, Federico Stasyszyn.
# License: BSD-3-Clause
#   Full Text: https://github.com/ivco19/brooks/blob/master/LICENSE


# =============================================================================
# IMPORTS
# =============================================================================

from django.db import models
from solo.models import SingletonModel


# =============================================================================
# MODELS
# =============================================================================

class ReportConfiguration(SingletonModel):
    class Meta:
        verbose_name = "Configuración de reporte"

    header = models.TextField(
        default="Generated with brooks", verbose_name="encabezado")
    footer = models.TextField(
        default="Generated at {{now}}", verbose_name="pie")
