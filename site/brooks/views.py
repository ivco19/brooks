import datetime as dt

from django.conf import settings

from django.views.generic.base import TemplateView

import mistune

import arcovid19

from libs.dmatplotlib import MatplotlibView

from brooks.views_mixins import LogginRequired

from libs import dmatplotlib as dplt

import matplotlib.pyplot as plt



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


class DashboardView(MatplotlibView):

    template_name = "Dashboard.html"

    def draw_plot(self, **kwargs):
        # vacio para que el context del mixin no explote
        pass

    def draw_grate_full_period_ar(self, cases, fig, ax, **kwargs):
        cases.plot.grate_full_period(
            ax=ax, confirmed=False, active=True,
            recovered=False, deceased=False)
        ax.legend(loc=2)

    def draw_grate_full_period_bs(self, cases, fig, ax, **kwargs):
        ax = cases.plot.grate_full_period(
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cases = arcovid19.load_cases()

        plot_methods = [
            self.draw_grate_full_period_ar,
            self.draw_grate_full_period_bs,
            self.draw_time_serie_all,
            self.draw_time_serie_ar,
            self.draw_barplot,
            self.draw_boxplot]
        plots = []

        for idx, pm in enumerate(plot_methods):
            plot = self.get_plot()
            fig, ax = plot.figaxes()
            pm(cases=cases, fig=fig, ax=ax, **kwargs)
            plots.append(plot)

        context["plots"] = plots
        return context






