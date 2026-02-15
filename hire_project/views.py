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
    if value is None: return None
    s = str(value).strip()
    return s if s else None

def _int_or_none(value):
    try:
        v = int(value)
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None

def _list_or_all(value):
    if not value or value == ["all"]: return ["all"]
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return ["all"]

def _get_owner_id(request):
    uid = request.session.get("uid")
    if not uid and settings.DEBUG:
        uid = "dev_test_user"   # ⚠️ dev only
    return uid

def _build_payload(data: dict, owner_id: str, status: str) -> dict:
    return {
        "title":           _str_or_none(data.get("title")),
        "objective":       _str_or_none(data.get("objective")),
        "description":     _str_or_none(data.get("description")),
        "org_name":        _str_or_none(data.get("org_name")),
        "org_type":        _str_or_none(data.get("org_type")),
        "org_dept":        _str_or_none(data.get("org_dept")),
        "start_date":      _str_or_none(data.get("start_date")),
        "deadline":        _str_or_none(data.get("deadline")),
        "age_range":       _str_or_none(data.get("age_range")),
        "gender":          _str_or_none(data.get("gender")) or "all",
        "occupations":     _list_or_all(data.get("occupations")),
        "location":        _str_or_none(data.get("location")),
        "sample_size":     _int_or_none(data.get("sample_size")),
        "question_count":  _int_or_none(data.get("question_count")),
        "est_minutes":     _int_or_none(data.get("est_minutes")),
        "owner_id": owner_id,
        "status":   status if status in ("active", "draft", "closed") else "draft",
    }

def _firestore_doc(payload: dict, django_id=None) -> dict:
    doc = {
        "title":        payload["title"],
        "objective":    payload["objective"],
        "description":  payload["description"],
        "org_name":     payload["org_name"],
        "org_type":     payload["org_type"],
        "org_dept":     payload["org_dept"],
        "start_date":   payload["start_date"],
        "deadline":     payload["deadline"],
        "target_group": {
            "age_range":   payload["age_range"],
            "gender":       payload["gender"],
            "occupations": payload.get("occupations", ["all"]),
            "location":    payload["location"],
        },
        "sample_size":     payload["sample_size"],
        "question_count": payload["question_count"],
        "est_minutes":     payload["est_minutes"],
        "owner_id":   payload["owner_id"],
        "status":     payload["status"],
        "updated_at": SERVER_TIMESTAMP,
    }
    if django_id: doc["django_id"] = str(django_id)
    return doc


# ═══════════════════════════════════════════════
#  Page views
# ═══════════════════════════════════════════════

def create_project_view(request):
    project_id = request.GET.get('project_id', '')
    existing_data = {}

    if project_id:
        try:
            db = get_firebase_db()
            doc = db.collection("projects").document(project_id).get()
            if doc.exists:
                data = doc.to_dict()
                
                # --- ส่วนที่เพิ่มเข้าไปเพื่อแก้ปัญหา TypeError ---
                for key, value in data.items():
                    # ตรวจสอบว่าเป็นฟิลด์วันที่หรือไม่ (DatetimeWithNanoseconds)
                    if hasattr(value, 'isoformat'):
                        data[key] = value.isoformat()
                    # ตรวจสอบข้อมูลใน nested dict (เช่น target_group)
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if hasattr(sub_value, 'isoformat'):
                                value[sub_key] = sub_value.isoformat()
                
                existing_data = data
                existing_data['id'] = doc.id
        except Exception as e:
            print(f"Error fetching project: {e}")

    return render(request, "hire/create_project.html", {
        # ใช้ json.dumps เพื่อส่งข้อมูลไปให้ JavaScript ใช้งานต่อได้
        "existing_data": json.dumps(existing_data), 
        "project_id": project_id
    })

# ... (draft_history_view, my_projects_view, project_list_view คงเดิม) ...

def draft_history_view(request):
    owner_id = _get_owner_id(request)
    if not owner_id: return redirect("login")
    drafts = ResearchDraft.objects.filter(owner_id=owner_id).order_by("-created_at")
    return render(request, "hire/draft_history.html", {"drafts": drafts})

def my_projects_view(request):
    owner_id = _get_owner_id(request)
    if not owner_id: return redirect("login")
    projects = ResearchProject.objects.filter(owner_id=owner_id).exclude(status="draft").order_by("-created_at")
    return render(request, "hire/my_projects.html", {"projects": projects})

def project_list_view(request):
    owner_id = _get_owner_id(request)
    if not owner_id: return redirect("login")
    projects = ResearchProject.objects.filter(owner_id=owner_id).order_by("-created_at")
    return render(request, "hire/project_list.html", {"projects": projects})


# ═══════════════════════════════════════════════
#  API: สร้าง / อัปเดตโครงการ
# ═══════════════════════════════════════════════

@csrf_exempt
def create_project_api(request):
    if request.method != "POST": return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    owner_id = _get_owner_id(request)
    if not owner_id: return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)

    if not _str_or_none(data.get("title")):
        return JsonResponse({"status": "error", "message": "กรุณาระบุชื่อโครงการ"}, status=400)

    status = data.get("status", "draft")
    payload = _build_payload(data, owner_id, status)
    
    # รับ project_id มาเพื่อเช็คว่าเป็นการ Update หรือไม่
    project_id = data.get("project_id")

    try:
        db = get_firebase_db()

        if status == "draft":
            # (Logic ส่วนบันทึก Draft เหมือนเดิม)
            draft = ResearchDraft.objects.create(**payload)
            db.collection("drafts").add(_firestore_doc(payload, django_id=draft.id))
            return JsonResponse({"status": "success", "draft_id": draft.id, "message": "บันทึกแบบร่างแล้ว"})

        else:
            # 1. บันทึก/อัปเดต Django
            if project_id:
                # กรณีอัปเดต: ค้นหาจาก Django ID ที่ผูกไว้ หรือ title/owner
                # (เพื่อความง่ายในตัวอย่างนี้จะเน้นไปที่การ Update Firestore)
                ResearchProject.objects.filter(title=payload['title'], owner_id=owner_id).update(**payload)
                
                # 2. อัปเดต Firestore
                doc_ref = db.collection("projects").document(project_id)
                doc_ref.update(_firestore_doc(payload))
                firebase_project_id = project_id
            else:
                # กรณีสร้างใหม่
                project = ResearchProject.objects.create(**payload)
                doc_data = _firestore_doc(payload, django_id=project.id)
                doc_data['created_at'] = SERVER_TIMESTAMP # เพิ่ม created_at เฉพาะตอนสร้างใหม่
                doc_ref = db.collection("projects").add(doc_data)
                firebase_project_id = doc_ref[1].id

            return JsonResponse({
                "status": "success", 
                "project_id": firebase_project_id, 
                "message": "บันทึกข้อมูลโครงการสำเร็จ"
            })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# ... (convert_to_project และ delete_draft คงเดิม) ...

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
        payload = _build_payload(draft.__dict__, draft.owner_id, "active")
        doc_data = _firestore_doc(payload, django_id=project.id)
        doc_data['created_at'] = SERVER_TIMESTAMP
        doc_ref = get_firebase_db().collection("projects").add(doc_data)
        draft.delete()
        return redirect(f"/survey/create-survey/?project_id={doc_ref[1].id}")
    except Exception as e:
        print(f"[Firebase ERROR] {e}")
        return redirect("my_projects")

def delete_draft(request, draft_id):
    try:
        ResearchDraft.objects.get(id=draft_id).delete()
    except ResearchDraft.DoesNotExist: pass
    return redirect("draft_history")