from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'mysite'

    def ready(self):
        import mysite.signals
