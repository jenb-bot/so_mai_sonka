from django.apps import AppConfig


class MedicamentsConfig(AppConfig):
    name = 'Medicaments'

    def ready(self):
        import Medicaments.signals
