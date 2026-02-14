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
    """คืน Firestore client — initialize เพียงครั้งเดียว"""
    if not firebase_admin._apps:
        cred_path = os.path.join(settings.BASE_DIR, "firebase_key.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    return firestore.client()


# ═══════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════

def _str_or_none(value) -> str | None:
    """คืน None ถ้า string ว่างเปล่าหรือ None"""
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def _int_or_none(value) -> int | None:
    """แปลงเป็น int หรือ None"""
    try:
        v = int(value)
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


def _build_project_payload(data: dict, owner_id: str, status: str) -> dict:
    """
    สร้าง dict ที่ใช้บันทึกทั้ง Django model และ Firestore
    รวม field ทั้งหมดที่สอดคล้องกับ schema v2.0
    """
    return {
        # ── ข้อมูลโครงการ ──────────────────────
        "title":       _str_or_none(data.get("title")),
        "objective":   _str_or_none(data.get("objective")),
        "description": _str_or_none(data.get("description")),

        # ── ข้อมูลองค์กร (NEW) ─────────────────
        "org_name": _str_or_none(data.get("org_name")),
        "org_type": _str_or_none(data.get("org_type")),
        "org_dept": _str_or_none(data.get("org_dept")),

        # ── ระยะเวลา (NEW) ──────────────────────
        "start_date": _str_or_none(data.get("start_date")),
        "deadline":   _str_or_none(data.get("deadline")),

        # ── กลุ่มตัวอย่าง ───────────────────────
        "age_range":   _str_or_none(data.get("age_range")),
        "gender":      _str_or_none(data.get("gender")) or "all",
        "location":    _str_or_none(data.get("location")),
        "sample_size": _int_or_none(data.get("sample_size")),

        # ── แบบสอบถาม (NEW) ────────────────────
        "question_count": _int_or_none(data.get("question_count")),
        "est_minutes":    _int_or_none(data.get("est_minutes")),

        # ── meta ────────────────────────────────
        "owner_id": owner_id,
        "status":   status if status in ("active", "draft", "closed") else "draft",
    }


def _build_firestore_doc(payload: dict, project_id=None) -> dict:
    """
    แปลง payload เป็น Firestore document
    - จัด target_group เป็น map
    - ใช้ SERVER_TIMESTAMP สำหรับ created_at
    - ลบ field ที่ไม่ต้องการออก
    """
    doc = {
        "title":       payload["title"],
        "objective":   payload["objective"],
        "description": payload["description"],

        "org_name": payload["org_name"],
        "org_type": payload["org_type"],
        "org_dept": payload["org_dept"],

        "start_date": payload["start_date"],
        "deadline":   payload["deadline"],

        # กลุ่มตัวอย่างเป็น map ตาม schema
        "target_group": {
            "age_range": payload["age_range"],
            "gender":    payload["gender"],
            "location":  payload["location"],
        },
        "sample_size": payload["sample_size"],

        "question_count": payload["question_count"],
        "est_minutes":    payload["est_minutes"],

        "owner_id":   payload["owner_id"],
        "status":     payload["status"],
        "created_at": SERVER_TIMESTAMP,   # ← Firebase Timestamp ไม่ใช่ string
    }

    if project_id:
        doc["project_id"] = str(project_id)

    return doc


# ═══════════════════════════════════════════════
#  Page views
# ═══════════════════════════════════════════════

def create_project_view(request):
    return render(request, "hire/create_project.html")


def survey_page(request):
    return render(request, "hire/create_survey.html")


def draft_history_view(request):
    drafts = ResearchDraft.objects.all().order_by("-created_at")
    return render(request, "hire/draft_history.html", {"drafts": drafts})


# ═══════════════════════════════════════════════
#  API: สร้าง / บันทึกโครงการ
# ═══════════════════════════════════════════════

@csrf_exempt
def create_project_api(request):
    """
    POST /hire/create-project-api/

    body (JSON):
        title, objective, description,
        org_name, org_type, org_dept,          ← NEW
        start_date, deadline,                   ← NEW
        age_range, gender, location, sample_size,
        question_count, est_minutes,            ← NEW
        status ("active" | "draft")
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    # owner_id: ในการใช้งานจริงดึงจาก request.user หรือ JWT
    owner_id = "demo_user_001"
    status   = data.get("status", "draft")

    # ── Validate ─────────────────────────────
    if not _str_or_none(data.get("title")):
        return JsonResponse({"status": "error", "message": "กรุณาระบุชื่อโครงการ"}, status=400)

    payload = _build_project_payload(data, owner_id, status)

    try:
        # ── บันทึกลง Django (PostgreSQL/SQLite) ──
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
            location       = payload["location"],
            sample_size    = payload["sample_size"] or 0,
            question_count = payload["question_count"],
            est_minutes    = payload["est_minutes"],
            status         = payload["status"],
            owner_id       = owner_id,
        )

        # ── Sync ไป Firestore ─────────────────
        db  = get_firebase_db()
        doc = _build_firestore_doc(payload, project_id=project.id)

        if status == "draft":
            # บันทึก projects
            proj_ref = db.collection("projects").document()
            proj_ref.set(doc)

            # บันทึก drafts (snapshot)
            draft_doc = {
                **doc,
                "project_id": proj_ref.id,
                # drafts ใช้ string timestamp ตาม schema
                "saved_at":   timezone.now().isoformat(),
                "created_at": timezone.now().isoformat(),
            }
            db.collection("drafts").add(draft_doc)

        else:
            # active: บันทึก projects เท่านั้น
            proj_ref = db.collection("projects").document()
            proj_ref.set(doc)

        return JsonResponse({
            "status":     "success",
            "project_id": project.id,
            "message":    "บันทึกแบบร่างแล้ว" if status == "draft" else "สร้างโครงการแล้ว",
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ═══════════════════════════════════════════════
#  convert draft → active project
# ═══════════════════════════════════════════════

def convert_to_project(request, draft_id):
    """
    แปลง draft เป็น active project
    - อัปเดต Django model
    - เพิ่มเอกสารใหม่ใน Firestore projects (ครบทุก field)
    - ลบ draft ทิ้ง
    """
    try:
        draft = ResearchDraft.objects.get(id=draft_id)
    except ResearchDraft.DoesNotExist:
        return JsonResponse({"status": "error", "message": "ไม่พบ draft นี้"}, status=404)

    # สร้าง project จาก draft
    project = ResearchProject.objects.create(
        title          = draft.title,
        objective      = getattr(draft, "objective", None),
        description    = draft.description,
        org_name       = getattr(draft, "org_name", None),
        org_type       = getattr(draft, "org_type", None),
        org_dept       = getattr(draft, "org_dept", None),
        start_date     = getattr(draft, "start_date", None),
        deadline       = getattr(draft, "deadline", None),
        age_range      = getattr(draft, "age_range", None),
        gender         = getattr(draft, "gender", "all"),
        location       = getattr(draft, "location", None),
        sample_size    = getattr(draft, "sample_size", 0) or 0,
        question_count = getattr(draft, "question_count", None),
        est_minutes    = getattr(draft, "est_minutes", None),
        owner_id       = getattr(draft, "owner_id", "anonymous"),
        status         = "active",
    )

    # Sync Firestore — ใช้ _build_firestore_doc เพื่อความสอดคล้อง
    payload = {
        "title": project.title, "objective": project.objective,
        "description": project.description,
        "org_name": project.org_name, "org_type": project.org_type,
        "org_dept": project.org_dept,
        "start_date": project.start_date, "deadline": project.deadline,
        "age_range": project.age_range, "gender": project.gender or "all",
        "location": project.location, "sample_size": project.sample_size,
        "question_count": project.question_count,
        "est_minutes": project.est_minutes,
        "owner_id": project.owner_id, "status": "active",
    }

    try:
        db = get_firebase_db()
        db.collection("projects").add(_build_firestore_doc(payload))
    except Exception as e:
        # log แต่ไม่ block การ redirect
        print(f"[Firebase ERROR] convert_to_project: {e}")

    draft.delete()
    return redirect("draft_history")