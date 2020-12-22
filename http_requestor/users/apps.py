from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "http_requestor.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            import http_requestor.users.signals  # noqa F401
        except ImportError:
            pass
