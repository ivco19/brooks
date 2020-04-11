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

    plot_kwargs = None
    subplots_kwargs = None

    def get_plot_kwargs(self):
        return self.plot_kwargs or {}

    def get_subplots_kwargs(self):
        return self.subplots_kwargs or {}

    def get_plot(self):
        """Return the plot to be injected in the context_data"""
        plot_kwargs = self.get_plot_kwargs()
        return subplots(**plot_kwargs)

    def draw_plot(self, fig, ax, **kwargs):
        """Draw the plot"""
        print('Grafico copado')
        raise NotImplementedError("Please implement the draw_plot method")

    def draw_plot1(self, fig, ax, **kwargs):
        """Draw the plot"""
        raise NotImplementedError("Please implement the draw_plot method")
    
    def draw_plot2(self, fig, ax, **kwargs):
        """Draw the plot"""
        raise NotImplementedError("Please implement the draw_plot method")

    def draw_plot3(self, fig, ax, **kwargs):
        """Draw the plot"""
        raise NotImplementedError("Please implement the draw_plot method")

    def draw_plot4(self, fig, ax, **kwargs):
        """Draw the plot"""
        raise NotImplementedError("Please implement the draw_plot method")

    def draw_plot5(self, fig, ax, **kwargs):
        """Draw the plot"""
        raise NotImplementedError("Please implement the draw_plot method")

    def get_context_data(self, **kwargs):
        """
        Overridden version of `.TemplateResponseMixin` to inject the plot into
        the template's context.
        """
        context = super().get_context_data(**kwargs)

        plot = self.get_plot()
        fig, ax = plot.figaxes(**self.get_subplots_kwargs())
        self.draw_plot(fig=fig, ax=ax, **kwargs)

        plot1 = self.get_plot()
        fig, ax = plot1.figaxes(**self.get_subplots_kwargs())
        self.draw_plot1(fig=fig, ax=ax, **kwargs)

        plot2 = self.get_plot()
        fig, ax = plot2.figaxes(**self.get_subplots_kwargs())
        self.draw_plot2(fig=fig, ax=ax, **kwargs)

        plot3 = self.get_plot()
        fig, ax = plot3.figaxes(**self.get_subplots_kwargs())
        self.draw_plot3(fig=fig, ax=ax, **kwargs)

        plot4 = self.get_plot()
        fig, ax = plot4.figaxes(**self.get_subplots_kwargs())
        self.draw_plot4(fig=fig, ax=ax, **kwargs)

        plot5 = self.get_plot()
        fig, ax = plot5.figaxes(**self.get_subplots_kwargs())
        self.draw_plot5(fig=fig, ax=ax, **kwargs)

        context = {"plot":plot, "plot1":plot1, "plot2":plot2, "plot3":plot3, "plot4":plot4, "plot5":plot5}
        return context


class MatplotlibView(MatplotlibMixin, TemplateView):
    pass


