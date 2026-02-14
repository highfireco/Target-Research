from django.shortcuts import render
from core.firebase_config import db
from datetime import datetime, timedelta, timezone

def survey_notification(request):
    # เปลี่ยน collection เป็น "projects"
    projects_ref = db.collection("projects")
    docs = projects_ref.stream()

    project_list = []
    now = datetime.now(tz=timezone.utc)  # <-- ทำให้ timezone-aware

    for doc in docs:
        data = doc.to_dict()

        created_at_obj = data.get("created_at")  # Firestore DatetimeWithNanoseconds
        if created_at_obj:
            created_at = created_at_obj  # already datetime with tzinfo
        else:
            continue  # ข้ามถ้าไม่มี created_at

        days_diff = (now - created_at).days
        is_new = days_diff <= 3

        expire_date = created_at + timedelta(days=10)
        days_left = max((expire_date - now).days, 0)  # กันติดลบ

        is_ending = 0 <= days_left <= 2

        project_list.append({
            "id": doc.id,
            "title": data.get("title"),
            "description": data.get("description"),
            "objective": data.get("objective"),
            "sample_size": data.get("sample_size"),
            "created_at": created_at,
            "is_new": is_new,
            "is_ending": is_ending,
            "days_left": days_left,
        })

    return render(request, "notifications/survey_notification.html", {
        "surveys": project_list
    })

def notification_home(request):
    return render(request, "notifications/notification_home.html")

def project_progress_notification(request):
    return render(request, "notifications/project_progress_notification.html")

def payment_notification(request):
    return render(request, "notifications/payment_notification.html")
