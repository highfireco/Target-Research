from django.apps import AppConfig

class DashboardPageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard_page'

    def ready(self):
        # initialize Firebase
        import core.firebase_config