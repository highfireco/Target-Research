from django.urls import path
from . import views  # ต้องมั่นใจว่า import views มาแล้ว

urlpatterns = [
    # แก้ไขให้รองรับ project_id ต่อท้าย URL
    path('project-summary/<str:project_id>/', views.payment_page, name='payment'),
]