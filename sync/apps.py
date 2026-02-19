from django.apps import AppConfig


class SyncConfig(AppConfig):
    name = 'sync'

    def ready(self):
        import sync.signals
