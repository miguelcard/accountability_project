from django.apps import AppConfig


class HabitsConfig(AppConfig):
    name = 'Models.habits'

    def ready(self):
        # Import signals module so receivers are registered
        import Models.habits.signals  # noqa: F401