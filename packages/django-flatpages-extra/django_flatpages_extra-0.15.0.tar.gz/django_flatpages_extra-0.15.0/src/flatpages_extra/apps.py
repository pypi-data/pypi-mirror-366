from django.apps import AppConfig


class FlatPagesPlusConfig(AppConfig):
    name = "flatpages_extra"
    verbose_name = "Flat Pages 💅"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import checks  # noqa: F401 (imported for registration)
