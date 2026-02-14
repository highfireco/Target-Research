from django.urls import path
from dashboard_page.views import survey_dashboard_view
<<<<<<< HEAD
from notifications.views import(
        notification_home,
        payment_notification,
        survey_notification,
        project_progress_notification
    )

urlpatterns = [
    path('dashboard-view/<str:survey_id>/', survey_dashboard_view, name='survey_dashboard'),
    path("notifications/", notification_home, name="notification_home"),
    path("payment/", payment_notification, name="payment_notification"),
    path("survey/", survey_notification, name="survey_notification"),
    path("project-progress/", project_progress_notification, name="project_progress_notification")
]
=======

urlpatterns = [
    path('dashboard-view/<str:survey_id>/', survey_dashboard_view, name='survey_dashboard'),
]

# from dashboard_page.views import verify_firebase
# urlpatterns += [
#     path('verify-db/', verify_firebase, name='verify_firebase'),
# ]
#
>>>>>>> 12bdc58dca73a90cc65b09fab8d55c25632dd2bc
