from django.urls import path
from dashboard.views import dashboard_view
urlpatterns = [
    path('', dashboard_view, name='dashboard'),
]

from dashboard.views import verify_firebase
urlpatterns += [
    path('verify-db/', verify_firebase, name='verify_firebase'),
]