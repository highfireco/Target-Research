from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from .models import ResearchDraft, ResearchProject

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import SERVER_TIMESTAMP

import json
import os


# ═══════════════════════════════════════════════
#  Firebase — initialize once
# ═══════════════════════════════════════════════

def get_firebase_db():
    if not firebase_admin._apps:
        cred_path = os.path.join(settings.BASE_DIR, "firebase_key.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    return firestore.client()


# ═══════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════

def _str_or_none(value):
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None

def _int_or_none(value):
    try:
        v = int(value)
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None

def _list_or_all(value):
    if not value or value == ["all"]:
        return ["all"]
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return ["all"]

def _get_owner_id(request):
    """ดึง uid จาก session — DEV fallback ถ้า DEBUG=True"""
    uid = request.session.get("uid")
    if not uid and settings.DEBUG:
        uid = "dev_test_user"   # ⚠️ dev only
    return uid

def _build_payload(data: dict, owner_id: str, status: str) -> dict:
    return {
        "title":          _str_or_none(data.get("title")),
        "objective":      _str_or_none(data.get("objective")),
        "description":    _str_or_none(data.get("description")),
        "org_name":       _str_or_none(data.get("org_name")),
        "org_type":       _str_or_none(data.get("org_type")),
        "org_dept":       _str_or_none(data.get("org_dept")),
        "start_date":     _str_or_none(data.get("start_date")),
        "deadline":       _str_or_none(data.get("deadline")),
        "age_range":      _str_or_none(data.get("age_range")),
        "gender":         _str_or_none(data.get("gender")) or "all",
        "occupations":    _list_or_all(data.get("occupations")),
        "location":       _str_or_none(data.get("location")),
        "sample_size":    _int_or_none(data.get("sample_size")),
        "question_count": _int_or_none(data.get("question_count")),
        "est_minutes":    _int_or_none(data.get("est_minutes")),
        "owner_id": owner_id,
        "status":   status if status in ("active", "draft", "closed") else "draft",
    }

def _firestore_doc(payload: dict, django_id=None) -> dict:
    doc = {
        "title":       payload["title"],
        "objective":   payload["objective"],
        "description": payload["description"],
        "org_name":    payload["org_name"],
        "org_type":    payload["org_type"],
        "org_dept":    payload["org_dept"],
        "start_date":  payload["start_date"],
        "deadline":    payload["deadline"],
        "target_group": {
            "age_range":   payload["age_range"],
            "gender":      payload["gender"],
            "occupations": payload.get("occupations", ["all"]),
            "location":    payload["location"],
        },
        "sample_size":    payload["sample_size"],
        "question_count": payload["question_count"],
        "est_minutes":    payload["est_minutes"],
        "owner_id":   payload["owner_id"],
        "status":     payload["status"],
        "created_at": SERVER_TIMESTAMP,
    }
    if django_id:
        doc["django_id"] = str(django_id)
    return doc


# ═══════════════════════════════════════════════
#  Page views
# ═══════════════════════════════════════════════

def create_project_view(request):
    return render(request, "hire/create_project.html")

def draft_history_view(request):
    owner_id = _get_owner_id(request)
    if not owner_id:
        return redirect("login")
    drafts = ResearchDraft.objects.filter(owner_id=owner_id).order_by("-created_at")
    return render(request, "hire/draft_history.html", {"drafts": drafts})

def my_projects_view(request):
    owner_id = _get_owner_id(request)
    if not owner_id:
        return redirect("login")
    projects = (
        ResearchProject.objects
        .filter(owner_id=owner_id)
        .exclude(status="draft")
        .order_by("-created_at")
    )
    return render(request, "hire/my_projects.html", {"projects": projects})

def project_list_view(request):
    owner_id = _get_owner_id(request)
    if not owner_id:
        return redirect("login")
    projects = ResearchProject.objects.filter(owner_id=owner_id).order_by("-created_at")
    return render(request, "hire/project_list.html", {"projects": projects})


# ═══════════════════════════════════════════════
#  API: สร้าง / บันทึกโครงการ
# ═══════════════════════════════════════════════

@csrf_exempt
def create_project_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    owner_id = _get_owner_id(request)
    if not owner_id:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)

    if not _str_or_none(data.get("title")):
        return JsonResponse({"status": "error", "message": "กรุณาระบุชื่อโครงการ"}, status=400)

    status  = data.get("status", "draft")
    payload = _build_payload(data, owner_id, status)

    try:
        db = get_firebase_db()

        if status == "draft":
            # บันทึก Django
            draft = ResearchDraft.objects.create(
                title          = payload["title"],
                objective      = payload["objective"],
                description    = payload["description"] or "",
                org_name       = payload["org_name"],
                org_type       = payload["org_type"],
                org_dept       = payload["org_dept"],
                start_date     = payload["start_date"],
                deadline       = payload["deadline"],
                age_range      = payload["age_range"],
                gender         = payload["gender"],
                occupations    = payload["occupations"],
                location       = payload["location"],
                sample_size    = payload["sample_size"] or 0,
                question_count = payload["question_count"],
                est_minutes    = payload["est_minutes"],
                status         = "draft",
                owner_id       = owner_id,
            )
            # Sync Firestore → collection "drafts"
            doc = _firestore_doc(payload, django_id=draft.id)
            doc["created_at"] = timezone.now().isoformat()  # drafts ใช้ string
            db.collection("drafts").add(doc)

            return JsonResponse({"status": "success", "draft_id": draft.id, "message": "บันทึกแบบร่างแล้ว"})

        else:
            # บันทึก Django
            project = ResearchProject.objects.create(
                title          = payload["title"],
                objective      = payload["objective"],
                description    = payload["description"],
                org_name       = payload["org_name"],
                org_type       = payload["org_type"],
                org_dept       = payload["org_dept"],
                start_date     = payload["start_date"],
                deadline       = payload["deadline"],
                age_range      = payload["age_range"],
                gender         = payload["gender"],
                occupations    = payload["occupations"],
                location       = payload["location"],
                sample_size    = payload["sample_size"] or 0,
                question_count = payload["question_count"],
                est_minutes    = payload["est_minutes"],
                status         = "active",
                owner_id       = owner_id,
            )
            # Sync Firestore → collection "projects"
            db.collection("projects").add(_firestore_doc(payload, django_id=project.id))

            return JsonResponse({"status": "success", "project_id": project.id, "message": "สร้างโครงการแล้ว"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ═══════════════════════════════════════════════
#  Convert draft → active
# ═══════════════════════════════════════════════

def convert_to_project(request, draft_id):
    try:
        draft = ResearchDraft.objects.get(id=draft_id)
    except ResearchDraft.DoesNotExist:
        return JsonResponse({"status": "error", "message": "ไม่พบ draft"}, status=404)

    project = ResearchProject.objects.create(
        title=draft.title, objective=draft.objective,
        description=draft.description, org_name=draft.org_name,
        org_type=draft.org_type, org_dept=draft.org_dept,
        start_date=draft.start_date, deadline=draft.deadline,
        age_range=draft.age_range, gender=draft.gender or "all",
        occupations=draft.occupations or ["all"],
        location=draft.location, sample_size=draft.sample_size or 0,
        question_count=draft.question_count, est_minutes=draft.est_minutes,
        owner_id=draft.owner_id, status="active",
    )

    try:
        payload = {
            "title": project.title, "objective": project.objective,
            "description": project.description, "org_name": project.org_name,
            "org_type": project.org_type, "org_dept": project.org_dept,
            "start_date": project.start_date, "deadline": project.deadline,
            "age_range": project.age_range, "gender": project.gender or "all",
            "occupations": project.occupations or ["all"],
            "location": project.location, "sample_size": project.sample_size,
            "question_count": project.question_count, "est_minutes": project.est_minutes,
            "owner_id": project.owner_id, "status": "active",
        }
        get_firebase_db().collection("projects").add(_firestore_doc(payload, django_id=project.id))
    except Exception as e:
        print(f"[Firebase ERROR] {e}")

    draft.delete()
    return redirect("my_projects")


# ═══════════════════════════════════════════════
#  ลบ Draft
# ═══════════════════════════════════════════════

def delete_draft(request, draft_id):
    try:
        ResearchDraft.objects.get(id=draft_id).delete()
    except ResearchDraft.DoesNotExist:
        pass
    return redirect("draft_history")