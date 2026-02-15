from django.urls import path
from dashboard_page.views import survey_dashboard_view
from notifications.views import(
        notification_home,
        payment_notification,
        survey_notification,
        project_progress_notification
    )
from Home_Layout.views import home_page

urlpatterns = [
    path('dashboard-view/<str:survey_id>/', survey_dashboard_view, name='survey_dashboard'),
    path("notifications/", notification_home, name="notification_home"),
    path("payment/", payment_notification, name="payment_notification"),
    path("survey/", survey_notification, name="survey_notification"),
    path("project-progress/", project_progress_notification, name="project_progress_notification"),
    path('home-page/', home_page, name='home_page'),
]
