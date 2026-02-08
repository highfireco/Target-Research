from django.urls import path
from .views import (
    create_project_view,
    create_project_api,
    survey_page,
)

urlpatterns = [
    path('create-project/', create_project_view, name='create_project'),
    path('create-project-api/', create_project_api, name='create_project_api'),
    path('create-survey/', survey_page, name='create_survey'),
]
