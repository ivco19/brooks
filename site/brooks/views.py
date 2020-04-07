import datetime as dt

from django.conf import settings

from django.views.generic.base import TemplateView

import mistune

import arcovid19

from libs.dmatplotlib import MatplotlibView

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


class AboutView(LogginRequired, MatplotlibView):

    template_name = "About.html"

    def draw_plot(self, fig, ax, **kwargs):
        cases = arcovid19.load_cases()
        cases.plot.grate_full_period(ax=ax)
        cases.plot.grate_full_period(ax=ax, provincia="cba")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with open(settings.ABOUT_PATH) as fp:
            src = fp.read()
        md = mistune.markdown(src.split("---")[0])
        context.update({"about": md})

        return context