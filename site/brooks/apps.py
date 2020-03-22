from django.apps import AppConfig


class BrooksConfig(AppConfig):
    name = 'brooks'

    def ready(self):
        import brooks.checks

