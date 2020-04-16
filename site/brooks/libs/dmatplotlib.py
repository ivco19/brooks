#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Arcovid-19 Brooks.
# Copyright (c) 2020, Juan B Cabral, Vanessa Daza, Diego García Lambas,
#                     Marcelo Lares, Nadia Luczywo, Dante Paz, Rodrigo Quiroga,
#                     Bruno Sanchez, Federico Stasyszyn.
# License: BSD-3-Clause
#   Full Text: https://github.com/ivco19/brooks/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""Wrapper around the matplotlib functionalities to write plots into a
django templates.

"""


# =============================================================================
# IMPORTS
# =============================================================================

import io
import base64

import matplotlib.pyplot as plt

from django.utils.html import format_html
from django.views.generic.base import TemplateView

import attr


# =============================================================================
# CLASSES BASE
# =============================================================================

@attr.s(frozen=True)
class DjangoMatplotlibWrapper:
    """This class are in charge of contain a figure and axes and write it
    to an HTML format.

    """

    fig = attr.ib()
    axes = attr.ib()
    plot_format = attr.ib()

    def get_img_png(self):
        buf = io.BytesIO()

        self.fig.savefig(buf, format='png')
        png = buf.getvalue()
        buf.close()

        png = base64.b64encode(png).decode("ascii")
        return f"<img src='data:image/png;base64,{png}'>"

    def get_img_svg(self):
        raise NotImplementedError()

    def to_html(self):
        def not_implemented_plot_format():
            raise NotImplementedError(f"Format unknown {self.plot_format}")
        key = f"get_img_{self.plot_format}"
        method = getattr(self, key, not_implemented_plot_format)
        img = method()
        return format_html(img)

    def figaxes(self):
        return self.fig, self.axes


# =============================================================================
# FUNCTIONS
# =============================================================================

def subplots(plot_format="png", *args, **kwargs):
    """This functions tries to mimic the behavior of
    matplotlib.pyplot.subplots but return a DjangoMatplotlibWrapper instead
    figure and axes.

    Also this functions receive in which format you want to write your plot
    in the HTML page.

    """
    fig, axes = plt.subplots(*args, **kwargs)
    return DjangoMatplotlibWrapper(plot_format=plot_format, fig=fig, axes=axes)


# =============================================================================
# VIEWS
# =============================================================================

class MatplotlibViewMixin:

    subplots_kwargs = None
    draw_methods = None
    plot_format = "png"
    tight_layout = False

    def get_subplots_kwargs(self):
        return self.subplots_kwargs or {}

    def get_plot(self):
        """Return the plot to be injected in the context_data"""
        splot_kwargs = self.get_subplots_kwargs()
        return subplots(plot_format=self.plot_format, **splot_kwargs)

    def get_tight_layout(self):
        """Return true if all the figures by default are tighned"""
        return bool(self.tight_layout)

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

            if self.get_tight_layout():
                fig.tight_layout()

            plots.append(plot)

        context["plot"] = plots[0]
        context["plots"] = plots
        return context


class MatplotlibView(MatplotlibViewMixin, TemplateView):
    pass
