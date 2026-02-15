from django.urls import path
from . import views

urlpatterns = [
    # แก้ไขให้รองรับ project_id ต่อท้าย URL
    path('project-summary/<str:project_id>/', views.payment_page, name='payment'),
]