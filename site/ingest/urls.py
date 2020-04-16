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

from ingest import views


# =============================================================================
# PATTERNS
# =============================================================================

urlpatterns = [
    path(
        'upload/',
        views.UploadRawFileView.as_view(),
        name='upload'),

    path(
        'chek_file/<int:pk>/',
        views.CheckRawFileView.as_view(),
        name='check_file'),

    path(
        'list_files/',
        views.ListRawFileView.as_view(),
        name='list_files'),

    path(
        'list_dmodel/<dmodel>/',
        views.ListDmodelView.as_view(),
        name='list_dmodel'),

    path(
        'plot_dmodel/<dmodel>/',
        views.PlotDmodelView.as_view(),
        name='plot_dmodel'),

    # path(
    #     'patient/<int:pk>/',
    #     views.PatientDetailView.as_view(),
    #     name='patient_detail')
]
