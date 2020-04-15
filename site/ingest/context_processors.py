from ingest import apps


def export_available_models(request):
    context = {
        "dmodels": apps.IngestConfig.dmodels.list_models()}
    return context
