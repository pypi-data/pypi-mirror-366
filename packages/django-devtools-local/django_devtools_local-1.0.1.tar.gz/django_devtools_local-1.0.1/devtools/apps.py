from django.apps import AppConfig


class DevtoolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'devtools'
    verbose_name = 'Django DevTools'
    
    def ready(self):
        """
        Configuration when the application starts
        """
        pass 