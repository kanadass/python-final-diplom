from django.apps import AppConfig


class BackendConfig(AppConfig):
    verbose_name = 'Бэкенд'
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

    def ready(self):
        """
        импортируем сигналы
        """
