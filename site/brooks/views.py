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

class PlotView(MatplotlibView):

    template_name = "dashboard.html"
    

    def draw_plot(self, fig, ax, **kwargs):
        cases = arcovid19.load_cases() 
        cases.plot(ax=ax, confirmed=False, active=True, recovered=False, deceased=False)
        ax.legend(loc=2)
   

    def draw_plot1(self, fig, ax, **kwargs):
        cases = arcovid19.load_cases() 
        ax = cases.plot.grate_full_period('Bs As', confirmed=True, active=True, recovered=True, deceased=True)


    def draw_plot2(self, fig, ax, **kwargs):
        cases = arcovid19.load_cases() 
        cases.plot.time_serie_all()


    def draw_plot3(self, fig, ax, **kwargs):
        cases = arcovid19.load_cases() 
        cases.plot.time_serie()


    def draw_plot4(self, fig, ax, **kwargs):
        cases = arcovid19.load_cases() 
        cases.plot.barplot()
        

    def draw_plot5(self, fig, ax, **kwargs):
        cases = arcovid19.load_cases() 
        cases.plot.boxplot(showfliers=False)






