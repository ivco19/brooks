from django.contrib import admin

from . import models as mdls

# =============================================================================
# LOCATIONS
# =============================================================================


@admin.register(mdls.RawFile)
class RawFileAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created", "modified", "confirmed")
    list_filter = ("created_by", "confirmed")


