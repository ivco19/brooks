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

import datetime as dt

from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.apps import apps

import jinja2

from brooks.views_mixins import LogginRequired

from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from reporter import models

# =============================================================================
# CONSTANTS
# =============================================================================

app = apps.get_app_config("ingest")


# =============================================================================
# CLASSES
# =============================================================================

class ReportView(LogginRequired, TemplateView):

    loggin_require_staff = True
    template_name = "reporter/ReportView.html"

    def get_context_data(self, **kwargs):
        report_conf = models.ReportConfiguration.get_solo()
        dmodels = app.ingestor.get_ingest_models()

        now = dt.datetime.now()
        context = {"now": now, "conf": report_conf, "models": dmodels}

        template = jinja2.Template(report_conf.get_template())
        report = template.render(context)

        context["report"] = report

        return context


class DownloadReportView(LogginRequired, View):

    loggin_require_staff = True

    def get(self, *args, **kwargs):
        report_conf = models.ReportConfiguration.get_solo()
        dmodels = app.ingestor.get_ingest_models()

        now = dt.datetime.now()
        context = {"now": now, "conf": report_conf, "models": dmodels}

        template = jinja2.Template(report_conf.get_template())
        report = template.render(context)

        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = (
            f"inline; filename=preport_brooks_{now.date().isoformat()}")

        font_config = FontConfiguration()
        HTML(string=report).write_pdf(response, font_config=font_config)

        return response
