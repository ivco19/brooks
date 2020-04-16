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

from django.apps import AppConfig
from django.conf import settings

from ingest.libs import mdesc


# =============================================================================
# CLASS
# =============================================================================

class IngestConfig(AppConfig):
    name = 'ingest'
    dmodels = mdesc.DynamicModels(settings.MODELS_DESCRIPTION)

    def ready(self):
        self.dmodels.create_models(self)
        self.dmodels.register_admin()
        import ingest.signals  # noqa
