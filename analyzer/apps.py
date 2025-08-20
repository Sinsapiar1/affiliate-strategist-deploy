from django.apps import AppConfig


class AnalyzerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analyzer'

    def ready(self):
        # Registrar señales para crear perfiles automáticamente
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
