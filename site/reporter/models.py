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

from django.db import models
from solo.models import SingletonModel


# =============================================================================
# CONSTANTS
# =============================================================================

HEADER_DEFAULT = """
<p>Generated with Brooks <code>{{now.isoformat()}}</code></p>
<hr>
"""

BODY_DEFAULT = """
<h1>Informe diario {{now.strftime('%Y-%m-%d')}}</h1>

{% for m in models %}
<div id="model-{{m.model_name()}}">
    <h2>{{ m.model_name() }}</h2>

    {{m.resume()}}

    {% for plot in m.plots.plot_all() %}
        {{ plot.to_html() }}
    {% endfor %}
    </div>
{% endfor %}
"""

FOOTER_DEFAULT = """
<hr>
<p>Generated with Brooks <code>{{now.isoformat()}}</code></p>
<p><a href="http://ivco19.github.io/">http://ivco19.github.io/</a></p>
"""

TEMPLATE = """
<div id="brooks-report">
    <div id="report-header" class="report-part">
        {header}
    </div>
    <div id="report-body" class="report-part">
        {body}
    </div>
    <footer id="report-footer" class="report-part">
        {footer}
    </footer>
</div>
"""


# =============================================================================
# MODELS
# =============================================================================

class ReportConfiguration(SingletonModel):
    class Meta:
        verbose_name = "Configuración de reporte"

    header = models.TextField(
        default=HEADER_DEFAULT, verbose_name="encabezado")
    body = models.TextField(
        default=BODY_DEFAULT, verbose_name="Cuerpo")
    footer = models.TextField(
        default=FOOTER_DEFAULT, verbose_name="pie")

    def get_template(self):
        return TEMPLATE.format(
            header=self.header, body=self.body, footer=self.footer)

