#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Arcovid-19 Brooks.
# Copyright (c) 2020, Juan B Cabral, Vanessa Daza, Diego García Lambas,
#                     Marcelo Lares, Nadia Luczywo, Dante Paz, Rodrigo Quiroga,
#                     Bruno Sanchez, Federico Stasyszyn.
# License: BSD-3-Clause
#   Full Text: https://github.com/ivco19/brooks/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""brooks URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


# =============================================================================
# IMPORTS
# =============================================================================

from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings

from django.contrib.auth import views as auth_views

from django.views.generic import RedirectView

from . import views


# =============================================================================
# PATTERNS
# =============================================================================

urlpatterns = [
    path(
        '',
        RedirectView.as_view(url='/dashboard', permanent=False),
        name="home"),

    path(
        'admin/',
        admin.site.urls),

    path(
        'login/',
        auth_views.LoginView.as_view()),
    path(
        'logout/',
        auth_views.LogoutView.as_view(), name="logout"),
    path(
        'summernote/',
        include('django_summernote.urls')),

    path(
        'changes/',
        views.ChangesView.as_view(),
        name='changes'),
    path(
        'about/',
        views.AboutView.as_view(),
        name='about'),
    path(
        'dashboard/',
        views.DashboardView.as_view(),
        name='dashboard'),

    path(
        'ingest/',
        include(('ingest.urls', 'ingest'), namespace='ingest')),
    path(
        'reporter/',
        include(('reporter.urls', 'reporter'), namespace='reporter')),
    path(
        'webtools/',
        include(('webtools.urls', 'webtools'), namespace='webtools')),

]


# =============================================================================
# DEBUG ONLY PATTERNS
# =============================================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_URL)
