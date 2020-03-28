import io
import base64
import functools

import matplotlib.pyplot as plt
from matplotlib.backends.backend_svg import FigureCanvas

from django.utils.html import format_html

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
