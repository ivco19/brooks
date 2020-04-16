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

from django.conf import settings


# =============================================================================
# FUNCTIONS
# =============================================================================

def export_some_settings(request):
    """Export some settings.py variables defined in settings.TO_EXPORT must
    be exported (sic.) to the templates.

    """
    context = {}

    for te in settings.TO_EXPORT:
        context[te] = getattr(settings, te, None)
    return context
