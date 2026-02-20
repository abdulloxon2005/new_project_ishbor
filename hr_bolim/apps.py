from django.apps import AppConfig

class HrBolimConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr_bolim'

    def ready(self):
        import hr_bolim.signals