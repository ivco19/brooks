from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import models as mdls

# =============================================================================
# TITLE
# =============================================================================

admin.site.site_header = _('Brooks Admin')

admin.site.site_title = _('Brooks Admin')

admin.site.index_title = _('Brooks Admin')


# =============================================================================
# LOCATIONS
# =============================================================================


@admin.register(mdls.RawFile)
class RawFileAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created", "modified", "confirmed")
    list_filter = ("created_by", "confirmed")


