from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from core.firebase_config import db # มั่นใจว่าเชื่อมต่อกับ target-research-6b556
from google.cloud import firestore

# ═══════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════

def _get_project_title(project_path):
    """ช่วยดึงชื่อ Title ของโปรเจกต์จาก Path ที่อ้างอิงไว้"""
    if not project_path:
        return "ไม่พบข้อมูลโครงการ"
    try:
        # ตัดเอา ID จาก Path เช่น "/projects/2D6E..." -> "2D6E..."
        proj_id = project_path.split('/')[-1]
        proj_doc = db.collection('projects').document(proj_id).get()
        if proj_doc.exists:
            return proj_doc.to_dict().get('title', "ไม่มีชื่อโครงการ")
    except Exception as e:
        print(f"DEBUG Error fetching project: {e}")
    return "ไม่พบข้อมูลโครงการ"


# ═══════════════════════════════════════════════
#  Views
# ═══════════════════════════════════════════════

# 1. ฟังก์ชันแสดงหน้าตัวอย่าง (Preview)
def survey_page(request, survey_id):
    survey_data = {}
    questions_list = []
    project_title = "ไม่พบข้อมูลโครงการ"
    survey_id = survey_id.strip() 
    
    try:
        survey_ref = db.collection('surveys').document(survey_id)
        survey_doc = survey_ref.get()
        
        if survey_doc.exists:
            survey_data = survey_doc.to_dict()
            
            # ดึงชื่อโปรเจกต์มาแสดงผล
            project_title = _get_project_title(survey_data.get('project_id'))

            # ดึงคำถามจาก Sub-collection 'questions' เรียงตามลำดับ (order)
            question_docs = survey_ref.collection('questions').order_by('order').stream()
            for doc in question_docs:
                q_data = doc.to_dict()
                q_data['id'] = doc.id
                questions_list.append(q_data)
    except Exception as e:
        print(f"DEBUG Error: {e}")

    return render(request, 'survey/survey_preview.html', {
        'survey': survey_data, 
        'questions': questions_list,
        'project_title': project_title  # ส่งชื่อโครงการไปแสดงที่ Header
    })

# 2. ฟังก์ชันแสดงหน้าสร้าง (Create)
def create_survey_page(request):
    project_id = request.GET.get('project_id', '')
    existing_data = {"title": "", "questions": []}

    if project_id:
        try:
            # ค้นหาแบบสอบถามเดิมที่ผูกกับโปรเจกต์นี้
            project_path = f"/projects/{project_id}"
            surveys = db.collection('surveys').where('project_id', '==', project_path).limit(1).get()

            if len(surveys) > 0:
                survey_doc = surveys[0]
                survey_dict = survey_doc.to_dict()
                existing_data["title"] = survey_dict.get("title", "")
                
                # ดึงคำถามจาก Sub-collection
                question_docs = survey_doc.reference.collection('questions').order_by('order').stream()
                for q_doc in question_docs:
                    existing_data["questions"].append(q_doc.to_dict())
        except Exception as e:
            print(f"Error: {e}")

    return render(request, "survey/create_survey.html", {
        'project_id': project_id,
        'existing_data': json.dumps(existing_data)
    })

@csrf_exempt
def save_survey_api(request):
    if request.method == "POST":
        try:
            # 1. 🚨 ดึง UID ของคนที่กำลัง Login จาก Session
            uid = request.session.get("uid")
            if not uid:
                return JsonResponse({"status": "error", "message": "กรุณาเข้าสู่ระบบก่อนสร้างแบบสอบถาม"}, status=401)

            data = json.loads(request.body)
            project_id = data.get("project_id")
            survey_title = data.get("survey_title")
            questions = data.get("questions", [])
            project_path = f"/projects/{project_id}"

            # ตรวจสอบว่ามีโปรเจกต์เดิมไหมเพื่อทำการ Update
            existing_surveys = db.collection('surveys').where('project_id', '==', project_path).limit(1).get()

            if len(existing_surveys) > 0:
                survey_ref = existing_surveys[0].reference
                # ลบคำถามเก่าออกก่อนอัปเดตใหม่
                old_questions = survey_ref.collection('questions').get()
                for old_q in old_questions:
                    old_q.reference.delete()
            else:
                survey_ref = db.collection('surveys').document()

            # 2. 🚨 แก้ไขก้อนข้อมูล survey_data ให้เพิ่ม owner_id เข้าไป
            survey_data = {
                'project_id': project_path,
                'title': survey_title,
                'status': "active",
                'owner_id': uid,  # <--- ✨ เพิ่มบรรทัดนี้ลงไป เพื่อระบุตัวตนคนสร้าง!
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            # เพิ่ม created_at เฉพาะตอนสร้างใหม่
            if len(existing_surveys) == 0:
                survey_data['created_at'] = firestore.SERVER_TIMESTAMP

            survey_ref.set(survey_data, merge=True)

            for q in questions:
                survey_ref.collection('questions').add({
                    'question_text': q['question_text'],
                    'question_type': q['question_type'],
                    'options': q['options'],
                    'order': q['order'],
                    'required': True
                })

            return JsonResponse({"status": "success", "survey_id": survey_ref.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

# 4. หน้าสำหรับผู้ใช้ทั่วไปตอบแบบสอบถาม

def survey_respond_page(request, survey_id):
    # ใช้ Logic เดียวกับ survey_page เพื่อดึงคำถามมาแสดง
    survey_data = {}
    questions_list = []
    survey_id = survey_id.strip()
    
    try:
        survey_ref = db.collection('surveys').document(survey_id)
        survey_doc = survey_ref.get()
        if survey_doc.exists:
            survey_data = survey_doc.to_dict()
            question_docs = survey_ref.collection('questions').order_by('order').stream()
            for doc in question_docs:
                q_data = doc.to_dict()
                q_data['id'] = doc.id
                questions_list.append(q_data)
    except Exception as e:
        print(f"Error: {e}")

    return render(request, 'survey/survey_respond.html', {
        'survey': survey_data, 
        'questions': questions_list,
        'survey_id': survey_id
    })

@csrf_exempt
def submit_response_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            survey_id = data.get("survey_id")
            answers = data.get("answers") # ลิสต์ของ {question_id, answer}

            # สร้าง Document ใหม่ในคอลเลกชัน responses
            # ตามโครงสร้างในรูป: answers (array), submitted_at, survey_id, user_id
            db.collection('responses').add({
                'survey_id': f"/surveys/{survey_id}",
                'answers': answers,
                'submitted_at': firestore.SERVER_TIMESTAMP,
                'user_id': "" # เว้นว่างไว้ตามรูปตัวอย่างของคุณ
            })

            return JsonResponse({"status": "success", "message": "ส่งแบบสอบถามเรียบร้อยแล้ว"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"error": "POST only"}, status=405)