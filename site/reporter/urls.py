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

from django.urls import path

from reporter import views


# =============================================================================
# PATTERNS
# =============================================================================

urlpatterns = [
    path(
        'download/',
        views.DownloadReportView.as_view(),
        name='download'),

    path(
        'view/',
        views.ReportView.as_view(),
        name='view')]
