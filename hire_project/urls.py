from django.urls import path
from hire_project.views import (
    create_project_view,
    create_project_api,
)
urlpatterns = [
    path('create-project/', create_project_view, name='create_project'),
    path('create-project-api/', create_project_api, name='create_project_api'),
]
