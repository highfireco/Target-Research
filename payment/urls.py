from django.urls import path
from . import views  # ต้องมั่นใจว่า import views มาแล้ว

urlpatterns = [
    # ... (path อื่นๆ ที่มีอยู่เดิม) ...
    
    # เพิ่มบรรทัดนี้ลงไปครับ
    path('beta-test/', views.beta_test_payment, name='beta_test_payment'),
]