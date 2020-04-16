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

from django.views.generic import UpdateView

from brooks.views_mixins import LogginRequired

from reporter import models, forms


# =============================================================================
# CLASSES
# =============================================================================

class ReportConfigurationView(LogginRequired, UpdateView):
    model = models.ReportConfiguration
    form_class = forms.ReportConfigurationForm
    template_name = "reporter/ReportConfiguration.html"
    success_message = "Configuración de reportes exitosa"

    def get_object(self):
        return models.ReportConfiguration.get_solo()
