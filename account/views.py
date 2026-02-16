from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from .models import EmailVerification
from .utils import generate_pin, send_pin_email
from firebase_admin import auth
from core.firebase_config import db
from django.views.decorators.csrf import csrf_exempt


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
        try:
            send_pin_email(email, pin)
            request.session["signup_email"] = email
            return redirect("verify_pin")
        except: Exception as e:
            print(f"email error {e}")
            return render(request, "account/signup.html", {
                "error": "ไม่สามารถส่งอีเมลได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง"
            })
        
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

        try:
            # 1. 🚨 ลองสร้าง User ใน Firebase Auth
            user = auth.create_user(email=email, password=password)
            
            # 2. บันทึก UID ลง Session และบังคับ Save ทันที
            request.session["firebase_uid"] = user.uid
            request.session.modified = True 
            
            # 3. ส่งไปหน้ากรอกประวัติ
            return redirect("create_account")
            
        except Exception as e:
            # 🚨 ถ้าสร้างไม่ได้ (เช่น เมลซ้ำ, รหัสสั้นไป) ให้โชว์ Error บนหน้าเว็บ
            print(f"🔥 Firebase Create User Error: {e}")
            return render(request, "account/set_password.html", {"error": str(e)})

    return render(request, "account/set_password.html")


def create_account(request):
    uid = request.session.get("firebase_uid")
    email = request.session.get("signup_email")

    if not uid:
        print("❌ ไม่มี UID ใน Session! กำลังเด้งกลับไปหน้า Signup")
        return redirect("signup")

    if request.method == "POST":
        try:
            name = request.POST.get("name")
            tel = request.POST.get("tel")
            age_range = request.POST.get("age_range")
            gender = request.POST.get("gender")
            occupation = request.POST.get("occupation")
            province = request.POST.get("province")

            # 🚨 ดักจับ Error ตอนบันทึกลงฐานข้อมูล Firestore
            db.collection("users").document(uid).set({
                "name": name,
                "email": email,  # แนะนำให้เก็บอีเมลไว้ใน DB ด้วยครับ
                "tel": tel,
                "age_range": age_range,
                "gender": gender,
                "occupation": occupation,
                "province": province
            })

            # สร้างโปรไฟล์เสร็จ ให้ล้างข้อมูลสมัครออกแล้วไปหน้า Login
            request.session.pop("signup_email", None)
            request.session.pop("email_verified", None)
            request.session.pop("firebase_uid", None)
            
            return redirect("login")
            
        except Exception as e:
            print(f"🔥 Firestore Save Error: {e}")
            return render(request, "account/create_account.html", {"error": "ไม่สามารถบันทึกข้อมูลได้"})

    return render(request, "account/create_account.html")


# login page
def login_view(request):
    return render(request, "account/login.html")


# verify Firebase token
@csrf_exempt
def verify_token(request):
    id_token = request.POST.get("idToken")
    
    # ดักจับกรณีไม่มี Token ส่งมา
    if not id_token:
        print("❌ No token received!")
        return JsonResponse({"status": "error", "message": "No token provided"})

    try:
        decoded = auth.verify_id_token(id_token)
        request.session["uid"] = decoded["uid"]
        print(id_token)
        return JsonResponse({"status": "success"})
    except Exception as e:
        # พิมพ์ Error ออกมาดูว่า Firebase บ่นอะไร
        print(f"🔥 Firebase Token Error: {e}") 
        return JsonResponse({"status": "error", "message": str(e)})
    

def dashboard_view(request):
    if not request.session.get("uid"):
        return redirect("login")
    return render(request, "home/home_preview.html")


def logout_view(request):
    request.session.flush()  # clears session
    return redirect("login")
