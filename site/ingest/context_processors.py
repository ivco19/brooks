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

from django.apps import apps

from ingest.models import BaseIngestModel

# =============================================================================
# CONSTANTS
# =============================================================================

app = apps.get_app_config("ingest")


# =============================================================================
# FUNCTIONS
# =============================================================================


def export_available_models(request):
    """Add the entire dictionary of dynamic models defined in the
    model descriptor file into the templates engine.

    """
    def dmodels_key(m):
        if m.principal:
            return ""
        return m.model_name()

    dmodels = [
        m for m in app.get_models()
        if issubclass(m, BaseIngestModel)]
    dmodels.sort(key=dmodels_key)

    context = {
        "dmodels": dmodels}
    return context
