from django.conf import settings
from django.views.generic.base import TemplateView

from brooks.views_mixins import LogginRequired


# =============================================================================
# VIEWS
# =============================================================================

class ShowView(LogginRequired, TemplateView):

    template_name = "webtools/Show.html"

    def get_context_data(self, tool, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(tool=tool, tool_url=settings.WEBTOOLS[tool])
        return context
