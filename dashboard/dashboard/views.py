from django.conf import settings

from django.views.generic.base import TemplateView

import mistune

#from .views_mixins import LogginRequired


# =============================================================================
# MISC
# =============================================================================

class ChangesView(TemplateView):

    template_name = "changes.html"

    def get_context_data(self):
        with open(settings.CHANGELOG_PATH) as fp:
            src = fp.read()
        md = mistune.markdown(src)

        return {"changelog": md}