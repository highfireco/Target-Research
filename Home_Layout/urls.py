from django.urls import path
from Home_Layout.views import ( home_page, )
urlpatterns = [ path('home-page/', home_page, name='home_page'),]