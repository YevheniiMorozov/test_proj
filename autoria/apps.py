from django.apps import AppConfig


class AutoriaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'autoria'

    def ready(self):
        import autoria.signals
