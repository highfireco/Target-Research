from django.urls import path
from Home_Layout.views import ( home_page,edit_profile, settings_view)

urlpatterns = [ 
    path('home-page/', home_page, name='home_page'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('settings/', settings_view, name='settings'),
    ]