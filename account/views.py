from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from .models import EmailVerification
from .utils import generate_pin, send_pin_email
from firebase_admin import auth
from core.firebase_config import db


# enter email
def signup_email(request):
    if request.method == "POST":
        email = request.POST.get("email")

        pin = generate_pin()
        EmailVerification.objects.update_or_create(
            email=email,
            defaults={
                "pin": pin,
                "created_at": timezone.now()
            }
        )

        send_pin_email(email, pin)
        request.session["signup_email"] = email
        return redirect("verify_pin")

    return render(request, "account/signup.html")


# verify PIN
from django.utils import timezone

def verify_pin(request):
    if request.method == "POST":
        email = request.session.get("signup_email")
        pin = request.POST.get("pin").strip()

        try:
            record = EmailVerification.objects.get(email=email)

            if record.pin.strip() == pin and not record.is_expired():
                request.session["email_verified"] = True
                return redirect("set_password")
            else:
                return render(request, "account/verify_email.html", {
                    "error": "Invalid or expired PIN"
                })

        except EmailVerification.DoesNotExist:
            return render(request, "account/verify_email.html", {
                "error": "Verification record not found"
            })

    return render(request, "account/verify_email.html")


# set password (Firebase Auth)
def set_password(request):
    email = request.session.get("signup_email")

    if not request.session.get("email_verified"):
        return redirect("signup")

    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            return render(request, "account/set_password.html",
                          {"error": "Passwords do not match"})

        user = auth.create_user(email=email, password=password)
        request.session["firebase_uid"] = user.uid
        return redirect("create_account")

    return render(request, "account/set_password.html")


def create_account(request):
    uid = request.session.get("firebase_uid")
    email = request.session.get("signup_email")

    if not uid:
        return redirect("signup")

    if request.method == "POST":
        name = request.POST.get("name")
        tel = request.POST.get("tel")

        db.collection("users").document(uid).set({
            "email": email,
            "name": name,
            "tel": tel,
        })

        return redirect("login")

    return render(request, "account/create_account.html")


# login page
def login_view(request):
    return render(request, "account/login.html")


# verify Firebase token
def verify_token(request):
    id_token = request.POST.get("idToken")

    try:
        decoded = auth.verify_id_token(id_token)
        request.session["uid"] = decoded["uid"]
        return JsonResponse({"status": "success"})
    except Exception:
        return JsonResponse({"status": "error"})
    

def dashboard_view(request):
    if not request.session.get("uid"):
        return redirect("login")
    return render(request, "account/dashboard_view.html")


def logout_view(request):
    request.session.flush()  # clears session
    return redirect("login")
