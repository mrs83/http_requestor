from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    name = 'http_requestor.core'
    verbose_name = _('Core')

    def ready(self):
        import http_requestor.core.signals  # noqa F401
