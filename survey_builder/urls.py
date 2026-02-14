from django.urls import path
from . import views

urlpatterns = [
    # หน้าสร้างแบบสอบถาม
    path('create-survey/', views.create_survey_page, name='create_survey'),
    # API สำหรับบันทึก
    path('save-survey-api/', views.save_survey_api, name='save_survey_api'),
    # หน้าพรีวิวที่เราทำไว้ก่อนหน้านี้
    path('survey-preview/<str:survey_id>/', views.survey_page, name='survey_preview'),
]