from django.urls import path
from Home_Layout.views import ( home_page, settings_view, edit_profile, delete_project)
from hire_project.views import create_project_view
from dashboard_page.views import survey_dashboard_view
from notifications.views import notification_home
from survey_builder.views import survey_respond_page

urlpatterns = [ 
    path('create-project/', create_project_view, name='create_project'),
    path('dashboard-view/<str:survey_id>/', survey_dashboard_view, name='survey_dashboard'),
    path('notification-home/', notification_home, name='notification_home'),
    path('home-page/', home_page, name='home_page'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('settings/', settings_view, name='settings'),
    path('respond/<str:survey_id>/', survey_respond_page, name='survey_respond'),
    path('delete-project/<str:survey_id>/', delete_project, name='delete_project'),
]