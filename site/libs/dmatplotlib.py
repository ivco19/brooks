import io
import base64
import functools

import matplotlib.pyplot as plt
from matplotlib.backends.backend_svg import FigureCanvas

from django.utils.html import format_html

from django.views.generic.base import TemplateView

import attr


@attr.s(frozen=True)
class DjangoMatplotlibWrapper:

    fig = attr.ib()
    axes = attr.ib()

    def get_png(self):
        buf = io.BytesIO()

        self.fig.savefig(buf, format='png')
        png = buf.getvalue()
        buf.close()
        return base64.b64encode(png).decode("ascii")

    def to_html(self):
        png = self.get_png()
        return format_html(f"<img src='data:image/png;base64,{png}'>")

    def figaxes(self):
        return self.fig, self.axes


@functools.wraps(plt.subplots)
def subplots(*args, **kwargs):
    fig, axes = plt.subplots(*args, **kwargs)
    return DjangoMatplotlibWrapper(fig, axes)


# =============================================================================
# VIEWS
# =============================================================================

class MatplotlibMixin:

    subplots_kwargs = None
    draw_methods = None

    def get_subplots_kwargs(self):
        return self.subplots_kwargs or {}

    def get_plot(self):
        """Return the plot to be injected in the context_data"""
        splot_kwargs = self.get_subplots_kwargs()
        return subplots(**splot_kwargs)

    def get_draw_methods(self):
        draw_methods = self.draw_methods or ["draw_plot"]
        methods = [getattr(self, m) for m in draw_methods]
        return methods

    def draw_plot(self, fig, ax, **kwargs):
        """Draw the plot"""
        raise NotImplementedError("Please implement the draw_plot method")

    def get_draw_context(self):
        "Returns a dictionary to be pased to all the draw_methods"
        return {}

    def get_context_data(self, **kwargs):
        """Overridden version of `.TemplateResponseMixin` to inject the
        plot into the template's context.
        """
        context = super().get_context_data(**kwargs)

        # inject the context info into the kwargs
        kwargs.update(self.get_draw_context())

        draw_methods = self.get_draw_methods()
        plots = []

        for dm in draw_methods:
            plot = self.get_plot()
            fig, ax = plot.figaxes()
            dm(fig=fig, ax=ax, **kwargs)
            plots.append(plot)

        context["plot"] = plots[0]
        context["plots"] = plots
        return context


class MatplotlibView(MatplotlibMixin, TemplateView):
    pass