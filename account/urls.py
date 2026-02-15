from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_email, name="signup"),
    path("verify/", views.verify_pin, name="verify_pin"),
    path("set-password/", views.set_password, name="set_password"),
    path("create_account/", views.create_account, name="create_account"),
    path("login/", views.login_view, name="login"),
    path("verify-token/", views.verify_token, name="verify_token"),
    path("logout/", views.logout_view, name="logout"),
]