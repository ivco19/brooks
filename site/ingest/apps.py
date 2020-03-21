from django.apps import AppConfig


class IngestConfig(AppConfig):
    name = 'ingest'

    def ready(self):
        import ingest.signals

