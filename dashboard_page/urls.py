from django.urls import path
from dashboard_page.views import dashboard_view

urlpatterns = [
    path('dashboard-view/', dashboard_view, name='dashboard'),
]

from dashboard_page.views import verify_firebase
urlpatterns += [
    path('verify-db/', verify_firebase, name='verify_firebase'),
]