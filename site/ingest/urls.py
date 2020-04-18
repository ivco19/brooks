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
        'download_empty/',
        views.DownloadEmptyView.as_view(),
        name='download_empty'),

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
        views.ListDModelView.as_view(),
        name='list_dmodel'),

    path(
        'plot_dmodel/<dmodel>/',
        views.PlotDModelView.as_view(),
        name='plot_dmodel'),

    path(
        'dmodel/<dmodel>/<int:pk>/',
        views.DetailDModelView.as_view(),
        name='dmodel_details')
]
