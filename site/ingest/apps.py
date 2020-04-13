from django.apps import AppConfig
from django.conf import settings

from libs import model_descriptions as mdesc


class IngestConfig(AppConfig):
    name = 'ingest'
    dmodels = mdesc.DynamicModels(settings.MODELS_DESCRIPTION)


    def ready(self):


        import ingest.signals






