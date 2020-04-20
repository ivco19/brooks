import datetime as dt

from django.conf import settings

from django.views.generic import TemplateView

import mistune

import arcovid19

from libs.dmatplotlib import MatplotlibView

from brooks.views_mixins import LogginRequired

from libs import dmatplotlib as dplt

import matplotlib.pyplot as plt

import logging

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
#from django.views.generic import TemplateView
import logging

from . import mapa

logger = logging.getLogger(__name__)



# =============================================================================
# MISC
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

class DashboardView(TemplateView):
    template_name = "Dashboard.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['mapa'] = mapa.mapa_arg()
        return context


class DashboardView_a(LogginRequired, MatplotlibView):   
    template_name = "Dashboard_a.html"

    draw_methods = [
        "drawg_curva_epi_pais",
        "drawg_curva_epi_pais_nor",
        "drawg_curva_epi_pais_log",
        "drawg_time_series_all",
        "drawg_barplot_all"
        ]
    plot_format = "png"

    def get_draw_context(self):
        return {"cases": arcovid19.load_cases()}
    
    def drawg_curva_epi_pais(self, cases, fig, ax, **kwargs):
        
        cases.plot.curva_epi_pais(ax=None, argentina=True,
        exclude=None, log=False, norm=False,
        paint='cuarentena', count_days='cuarentena')

    def drawg_curva_epi_pais_nor(self, cases, fig, ax, **kwargs):
        cases.plot.curva_epi_pais(ax=None, argentina=True,
        exclude=None, log=False, norm=True,
        paint=None, count_days=None)

    def drawg_curva_epi_pais_log(self, cases, fig, ax, **kwargs):
        cases.plot.curva_epi_pais(ax=None, argentina=True,
        exclude=None, log=True, norm=False,
        paint=None, count_days=None)

    def drawg_time_series_all(self, cases, fig, ax, **kwargs):
        cases.plot.time_serie_all()

    def drawg_barplot_all(self, cases, fig, ax, **kwargs):
        cases.plot.barplot()


class DashboardView_c(LogginRequired, MatplotlibView):
    template_name = "Dashboard_c.html"

    draw_methods = [
        "drawg_curva_epi_provincia",
        "drawg_curva_epi_provincia_nor",
        "drawg_curva_epi_provincia_log",
        "drawg_time_series_cba",
        "drawg_barplot_cba"
        ]
    plot_format = "png"

    def get_draw_context(self):
        return {"cases": arcovid19.load_cases()}
    
    def drawg_curva_epi_provincia(self, cases, fig, ax, **kwargs):
        cases.plot.curva_epi_provincia(
            "cordoba", confirmed=True,
            active=True, recovered=True, deceased=True,
            ax=None,
            log=False, norm=False,
            color=None, alpha=None,
            linewidth=None, linestyle=None,
            marker=None, markerfacecolor=None,
            markeredgewidth=None,
            markersize=None, markevery=None)

    def drawg_curva_epi_provincia_nor(self, cases, fig, ax, **kwargs):
        cases.plot.curva_epi_provincia(
            "cordoba", confirmed=True,
            active=True, recovered=True, deceased=True,
            ax=None,
            log=False, norm=True,
            color=None, alpha=None,
            linewidth=None, linestyle=None,
            marker=None, markerfacecolor=None,
            markeredgewidth=None,
            markersize=None, markevery=None)

    def drawg_curva_epi_provincia_log(self, cases, fig, ax, **kwargs):
        cases.plot.curva_epi_provincia(
            "cordoba", confirmed=True,
            active=True, recovered=True, deceased=True,
            ax=None,
            log=True, norm=False,
            color=None, alpha=None,
            linewidth=None, linestyle=None,
            marker=None, markerfacecolor=None,
            markeredgewidth=None,
            markersize=None, markevery=None)

    def drawg_time_series_cba(self, cases, fig, ax, **kwargs):
        cases.plot.time_serie("cordoba", ax=ax)

    def drawg_barplot_cba(self, cases, fig, ax, **kwargs):
        cases.plot.barplot("cordoba", ax=ax)
