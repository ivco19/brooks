from django.conf import settings

from django.views.generic.base import TemplateView

import mistune

from .views_mixins import LogginRequired


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

    def get_context_data(self):
        with open(settings.ABOUT_PATH) as fp:
            src = fp.read()
        md = mistune.markdown(src.split("---")[0])
        return {"about": md}