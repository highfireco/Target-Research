from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
from core.firebase_config import db 
from google.cloud import firestore

# ═══════════════════════════════════════════════
#  Helpers: จัดการข้อมูลก่อนส่ง/บันทึก
# ═══════════════════════════════════════════════

def _serialize_firebase_data(data):
    """ แปลง DatetimeWithNanoseconds เป็น ISO string เพื่อให้ JSON serializable """
    for key, value in data.items():
        if hasattr(value, 'isoformat'):
            data[key] = value.isoformat()
        elif isinstance(value, dict):
            _serialize_firebase_data(value)
    return data

def _get_owner_id(request):
    uid = request.session.get("uid")
    if not uid and settings.DEBUG:
        uid = "dev_test_user"
    return uid

# ═══════════════════════════════════════════════
#  Page Views: แสดงผลหน้าเว็บ
# ═══════════════════════════════════════════════

def create_project_view(request):
    """ หน้าสร้าง/แก้ไขโปรเจกต์ พร้อมระบบ Auto-fill ข้อมูลเดิม """
    project_id = request.GET.get('project_id', '')
    existing_data = {}

    if project_id:
        try:
            doc = db.collection("projects").document(project_id).get()
            if doc.exists:
                data = doc.to_dict()
                existing_data = _serialize_firebase_data(data) # กัน Error วันที่
                existing_data['id'] = doc.id
        except Exception as e:
            print(f"Error fetching project: {e}")

    return render(request, "hire/create_project.html", {
        "existing_data": json.dumps(existing_data),
        "project_id": project_id
    })

def payment_page(request, project_id):
    """ หน้าสรุปโครงการและค่าใช้จ่าย (ดึงข้อมูลจากทั้ง Projects และ Surveys) """
    try:
        # 1. ดึงข้อมูลโครงการ
        project_doc = db.collection("projects").document(project_id).get()
        if not project_doc.exists:
            return render(request, "404.html")
        
        project_data = project_doc.to_dict()
        
        # 2. ดึงข้อมูลแบบสอบถามที่ผูกกับโปรเจกต์นี้
        project_path = f"/projects/{project_id}"
        survey_query = db.collection("surveys").where("project_id", "==", project_path).limit(1).get()
        
        question_count = 0
        if len(survey_query) > 0:
            # นับจำนวนคำถามจาก sub-collection 'questions'
            questions = survey_query[0].reference.collection("questions").get()
            question_count = len(questions)

        # 3. คำนวณค่าใช้จ่าย
        sample_size = int(project_data.get("sample_size") or 0)
        incentive = sample_size * 50 # สมมติ 50 บาทต่อคน
        fee = 5000
        vat = (incentive + fee) * 0.07
        
        context = {
            "project": project_data,
            "project_id": project_id,
            "question_count": question_count,
            "pricing": {
                "incentive": incentive,
                "fee": fee,
                "vat": vat,
                "total": incentive + fee + vat
            }
        }
        return render(request, "payment/payment.html", context)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ═══════════════════════════════════════════════
#  API Views: จัดการข้อมูลในฐานข้อมูล
# ═══════════════════════════════════════════════

@csrf_exempt
def create_project_api(request):
    """ API สำหรับบันทึกหรืออัปเดตโครงการ """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
        project_id = data.get("project_id")
        owner_id = _get_owner_id(request)
        
        # เตรียมข้อมูลสำหรับบันทึก
        payload = {
            "title": data.get("title"),
            "objective": data.get("objective"),
            "description": data.get("description"),
            "org_name": data.get("org_name"),
            "org_type": data.get("org_type"),
            "target_group": {
                "age_range": data.get("age_range"),
                "gender": data.get("gender"),
                "occupations": data.get("occupations", ["all"]),
                "location": data.get("location")
            },
            "sample_size": data.get("sample_size"),
            "question_count": data.get("question_count"),
            "est_minutes": data.get("est_minutes"),
            "owner_id": owner_id,
            "status": data.get("status", "active"),
            "updated_at": firestore.SERVER_TIMESTAMP
        }

        if project_id:
            # --- กรณี Update ข้อมูลเดิม ---
            doc_ref = db.collection("projects").document(project_id)
            doc_ref.update(payload)
            firebase_id = project_id
        else:
            # --- กรณี Create ข้อมูลใหม่ ---
            payload["created_at"] = firestore.SERVER_TIMESTAMP
            doc_ref = db.collection("projects").add(payload)
            firebase_id = doc_ref[1].id

        return JsonResponse({"status": "success", "project_id": firebase_id})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)