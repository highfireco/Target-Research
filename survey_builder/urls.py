from django.urls import path
from . import views

urlpatterns = [
    # หน้าสำหรับสร้างแบบสอบถาม (รองรับการรับ ?project_id=... ผ่าน URL)
    path('create-survey/', views.create_survey_page, name='create_survey'),
    
    # API สำหรับบันทึกโครงสร้างแบบสอบถามลง Firebase
    path('save-survey-api/', views.save_survey_api, name='save_survey_api'),
    
    # หน้าพรีวิวสำหรับเจ้าของโปรเจกต์ (ดึงชื่อโปรเจกต์มาโชว์ที่หัว)
    path('survey-preview/<str:survey_id>/', views.survey_page, name='survey_preview'),
    path('respond/<str:survey_id>/', views.survey_respond_page, name='survey_respond'),
    path('submit-response-api/', views.submit_response_api, name='submit_response_api'),

]