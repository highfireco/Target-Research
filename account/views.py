from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from .models import EmailVerification
from .utils import generate_pin, send_pin_email
from firebase_admin import auth
from core.firebase_config import db
import re


# enter email
def signup_email(request):
    if request.method == "POST":
        email = request.POST.get("email")

        # Check if email already exists in Firebase
        try:
            auth.get_user_by_email(email)
            return render(request, "account/signup.html", {
                "error": "This email is already registered. Please login instead."
            })
        except auth.UserNotFoundError:
            pass  # email is available

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

        # password rules
        if len(password) < 12 or len(password) > 16:
            return render(request, "account/set_password.html", {
                "error": "Password must be 12–16 characters long"
            })

        if not re.search(r"[A-Z]", password):
            return render(request, "account/set_password.html", {
                "error": "Password must include at least one uppercase letter"
            })

        if not re.search(r"[a-z]", password):
            return render(request, "account/set_password.html", {
                "error": "Password must include at least one lowercase letter"
            })

        if not re.search(r"\d", password):
            return render(request, "account/set_password.html", {
                "error": "Password must include at least one number"
            })

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\\[\]]", password):
            return render(request, "account/set_password.html", {
                "error": "Password must include at least one symbol"
            })

        if password != confirm:
            return render(request, "account/set_password.html", {
                "error": "Passwords do not match"
            })
        
        # create Firebase user
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
        if not name or not re.match(r'^[A-Za-zก-๙\s]+$', name):
            return render(request, "account/create_account.html", {
                "error": "Name must contain only letters"
            })
        tel = request.POST.get("tel")
        if not re.match(r'^[0-9]{9,10}$', tel):
            return render(request, "account/create_account.html", {
                "error": "Telephone must be 9–10 digits"
            })
        age_range = request.POST.get("age_range")
        gender = request.POST.get("gender")
        occupation = request.POST.get("occupation")
        occupation_other = request.POST.get("occupation_other")
        if occupation == "Other" and occupation_other:
            occupation = occupation_other
        province = request.POST.get("province")

        db.collection("users").document(uid).set({
            "name": name,
            "tel": tel,
            "age_range": age_range,
            "gender": gender,
            "occupation": occupation,
            "province": province
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
    

def home_preview(request):
    if not request.session.get("uid"):
        return redirect("login")
    return render(request, "home/home_preview.html")


def logout_view(request):
    request.session.flush()  # clears session
    return redirect("login")