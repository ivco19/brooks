from django.contrib import admin

from . import models as mdls

# =============================================================================
# FILES
# =============================================================================

class EventInline(admin.StackedInline):
    verbose_name_plural = "Eventos"
    list_display = ("id", "indice_archivo", "id_archivo")
    model = mdls.Event




@admin.register(mdls.RawFile)
class RawFileAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created", "modified", "confirmed", "is_parsed")
    list_filter = ("created_by", "confirmed", "is_parsed")

    #inlines = (EventInline,)



@admin.register(mdls.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "status")
    #list_filter = ("created_by", "confirmed", "is_parsed")