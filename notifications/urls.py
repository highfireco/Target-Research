from django.urls import path
from .views import (
    notification_home,
    payment_notification,
    survey_notification,
    project_progress_notification,
)


urlpatterns = [
    path("", notification_home, name="notification_home"),
    path("payment/", payment_notification, name="payment_notification"),
    path("survey/", survey_notification, name="survey_notification"),
    path("project-progress/", project_progress_notification, name="project_progress_notification"),
]
