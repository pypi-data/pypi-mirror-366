from django.apps import AppConfig


class LogHubConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'log_hub'
    verbose_name = 'Log Hub'
    
    def ready(self):
        # Import signals if you have any
        pass
    