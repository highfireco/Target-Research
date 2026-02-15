from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from core.firebase_config import db # มั่นใจว่าเชื่อมต่อกับ target-research-6b556
from google.cloud import firestore

# 1. ฟังก์ชันแสดงหน้าตัวอย่าง (Preview)
def survey_page(request, survey_id):
    survey_data = {}
    questions_list = []
    # ตัดช่องว่างและตรวจสอบ Case-sensitivity (เช่นตัว w เล็ก)
    survey_id = survey_id.strip() 
    
    try:
        survey_ref = db.collection('surveys').document(survey_id)
        survey_doc = survey_ref.get()
        
        if survey_doc.exists:
            survey_data = survey_doc.to_dict()
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
        'questions': questions_list
    })

# 2. ฟังก์ชันแสดงหน้าสร้าง (Create)
def create_survey_page(request):
    return render(request, "survey/create_survey.html")

# 3. API สำหรับบันทึกคำถามลง Firebase
@csrf_exempt
def save_survey_api(request):
    data = json.loads(request.body)
    survey_id = data.get("survey_id")
    project_id = data.get("project_id") # รับค่าไอดีโปรเจกต์มาด้วย

    survey_ref = db.collection('surveys').document(survey_id)
    survey_ref.update({
        'project_id': f"/projects/{project_id}", # บันทึกการเชื่อมโยง
        'updated_at': firestore.SERVER_TIMESTAMP
    })

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # ใช้ ID จริงจากระบบของคุณ (GXWpYH51w91KUfxjzqGS)
            survey_id = data.get("survey_id", "GXWpYH51w91KUfxjzqGS") 
            questions = data.get("questions", [])

            survey_ref = db.collection('surveys').document(survey_id)
            
            for q in questions:
                # บันทึกข้อมูลคำถามแต่ละข้อลงใน Sub-collection
                survey_ref.collection('questions').add({
                    'question_text': q['question_text'],
                    'question_type': q['question_type'],
                    'options': q['options'],
                    'order': q['order'],
                    'required': True
                })

            return JsonResponse({"status": "success", "survey_id": survey_id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"error": "POST only"}, status=405)