from django.urls import path
from Home_Layout.views import ( home_page,)
from hire_project.views import create_project_view
from dashboard_page.views import survey_dashboard_view
from notifications.views import notification_home

urlpatterns = [ 
    path('home-page/', home_page, name='home_page'),
    path('create-project/', create_project_view, name='create_project'),
    path('dashboard-view/<str:survey_id>/', survey_dashboard_view, name='survey_dashboard'),
    path('notification-home/', notification_home, name='notification_home'),
]