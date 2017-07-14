from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class BlogConfig(AppConfig):
    name = 'blog'

    def ready(self):
        import blog.signals


