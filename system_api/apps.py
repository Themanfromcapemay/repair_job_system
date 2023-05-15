from django.apps import AppConfig


class SystemApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'system_api'

    def ready(self):
        import system_api.signals  # Replace 'your_app_name' with your actual app name
