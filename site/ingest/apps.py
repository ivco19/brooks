from django.apps import AppConfig
from django.conf import settings

from ingest.libs import mdesc


class IngestConfig(AppConfig):
    name = 'ingest'
    dmodels = mdesc.DynamicModels(settings.MODELS_DESCRIPTION)

    def ready(self):
        self.dmodels.create_models(self)
        self.dmodels.register_admin()
        import ingest.signals  # noqa
