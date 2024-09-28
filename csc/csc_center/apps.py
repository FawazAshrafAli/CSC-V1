from django.apps import AppConfig


class CscCenterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'csc_center'

    def ready(self):
        # Import celery app now that Django is mostly ready.
        # This initializes Celery and autodiscovers tasks
        import csc.celery