from django.urls import path
from . import views

urlpatterns = [
    path("", views.project_summary, name="project_summary"),
    path("payment/", views.payment_page, name="payment"),
]
