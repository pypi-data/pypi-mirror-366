from django.apps import AppConfig


class VersionControlConfig(AppConfig):
    name = "version_control"
    verbose_name = "Контроль версий"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import version_control.signals
