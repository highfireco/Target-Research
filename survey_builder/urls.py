from django.urls import path
from survey_builder.views import (
    survey_page
)
urlpatterns = [
    path('survey-page/', survey_page, name='survey_page'),
]
