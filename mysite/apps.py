from django.apps import AppConfig


class MysiteConfig(AppConfig):
    name = 'mysite'

    def ready(self):
        import mysite.signals
