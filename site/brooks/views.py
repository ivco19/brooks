import datetime as dt

from django.conf import settings

from django.views.generic.base import TemplateView

import mistune

import arcovid19

from libs import dmatplotlib as dplt

from brooks.views_mixins import LogginRequired


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

    def get_plot(self):
        cases = arcovid19.load_cases().df

        prov = "CBA"
        prov_c = cases[cases.provincia_status == f"{prov}_C"]
        columns = [c for c in prov_c.columns if isinstance(c, dt.datetime)]

        plot = dplt.subplots()
        fig, ax = plot.figaxes()

        values = prov_c[columns].values.flatten()
        ax.plot(values, label="Casos nuevos")

        ticks = [str(c.date()) for c in columns]
        ax.set_xticklabels(ticks, rotation=75)

        ax.set_title("Infectados por Día")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Personas")

        fig.legend()

        return plot


    def get_context_data(self):
        plot = self.get_plot()

        with open(settings.ABOUT_PATH) as fp:
            src = fp.read()
        md = mistune.markdown(src.split("---")[0])

        return {"about": md, "plot": plot}