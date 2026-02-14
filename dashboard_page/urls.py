from django.urls import path
from dashboard_page.views import survey_dashboard_view

urlpatterns = [
    path('dashboard-view/<str:survey_id>/', survey_dashboard_view, name='survey_dashboard'),
]

# from dashboard_page.views import verify_firebase
# urlpatterns += [
#     path('verify-db/', verify_firebase, name='verify_firebase'),
# ]
#