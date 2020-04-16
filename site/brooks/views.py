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

import mistune

import arcovid19

from brooks.libs.dmatplotlib import MatplotlibView

from brooks.views_mixins import LogginRequired


# =============================================================================
# CLASSES
# =============================================================================

class ChangesView(LogginRequired, TemplateView):

    template_name = "Changes.html"

    def get_context_data(self):
        with open(settings.CHANGELOG_PATH) as fp:
            src = fp.read()
        md = mistune.markdown(src)
        return {"changelog": md}


class AboutView(LogginRequired, TemplateView):

    template_name = "About.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with open(settings.ABOUT_PATH) as fp:
            src = fp.read()
        md = mistune.markdown(src.split("---")[0])
        context.update({"about": md})

        return context


class DashboardView(LogginRequired, MatplotlibView):

    template_name = "Dashboard.html"
    draw_methods = [
        "draw_grate_full_period_ar",
        "draw_grate_full_period_bs",
        "draw_time_serie_all",
        "draw_time_serie_ar",
        "draw_barplot",
        "draw_boxplot"]
    plot_format = "png"
    tight_layout = True

    def get_draw_context(self):
        return {"cases": arcovid19.load_cases()}

    def draw_grate_full_period_ar(self, cases, fig, ax, **kwargs):
        cases.plot.grate_full_period(
            ax=ax, confirmed=False, active=True,
            recovered=False, deceased=False)
        ax.legend(loc=2)

    def draw_grate_full_period_bs(self, cases, fig, ax, **kwargs):
        cases.plot.grate_full_period(
            'Bs As', ax=ax, confirmed=True, active=True,
            recovered=True, deceased=True)

    def draw_time_serie_all(self, cases, fig, ax, **kwargs):
        cases.plot.time_serie_all(ax=ax)

    def draw_time_serie_ar(self, cases, fig, ax, **kwargs):
        cases.plot.time_serie(ax=ax)

    def draw_barplot(self, cases, fig, ax, **kwargs):
        cases.plot.barplot(ax=ax)

    def draw_boxplot(self, cases, fig, ax, **kwargs):
        cases.plot.boxplot(showfliers=False, ax=ax)
