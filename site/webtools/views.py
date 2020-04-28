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
from django.views.generic.base import TemplateView

from brooks.views_mixins import LogginRequired


# =============================================================================
# VIEWS
# =============================================================================

class ShowView(LogginRequired, TemplateView):

    require_staff = True
    template_name = "webtools/Show.html"

    def get_context_data(self, tool, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(tool=tool, tool_url=settings.WEBTOOLS[tool])
        return context
