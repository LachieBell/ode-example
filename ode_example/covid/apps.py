from django.apps import AppConfig


class CovidConfig(AppConfig):
    name = 'covid'

    def ready(self):
        import covid.signals
