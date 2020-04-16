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

from ingest import apps


# =============================================================================
# FUNCTIONS
# =============================================================================

def export_available_models(request):
    """Add the entire dictionary of dynamic models defined in the
    model descriptor file into the templates engine.

    """
    context = {
        "dmodels": apps.IngestConfig.dmodels.list_models()}
    return context
