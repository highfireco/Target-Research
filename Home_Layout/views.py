from django.shortcuts import render, redirect
from core.firebase_config import db # อย่าลืม import db
from django.contrib import messages

def home_page(request):
    uid = request.session.get("uid")
    if not uid:
        return redirect("login")

    # 1. หมวด "งานวิจัยของฉัน" (My Research)
    my_surveys_ref = db.collection('surveys').where('owner_id', '==', uid).stream()
    my_researches = []
    for doc in my_surveys_ref:
        data = doc.to_dict()
        data['id'] = doc.id
        my_researches.append(data)

    # 2. หมวด "แบบสอบถามที่เปิดรับคำตอบ" (Available Surveys)
    all_surveys_ref = db.collection('surveys').stream()
    available_surveys = []
    for doc in all_surveys_ref:
        data = doc.to_dict()
        data['id'] = doc.id
        if data.get('owner_id') != uid and data.get('status') == 'active':
            available_surveys.append(data)

    # 3. ส่งตัวแปรไปให้หน้า HTML
    context = {
        'researches': my_researches, 
        'first_survey': my_researches[0] if my_researches else None,
        'available_surveys': available_surveys  # 👈 เช็คให้ชัวร์ว่ามีบรรทัดนี้ ไม่งั้น HTML จะไม่มีข้อมูล
    }
    return render(request, 'home/home_preview.html', context)

def delete_project(request, survey_id):
    uid = request.session.get("uid")
    if not uid:
        return redirect("login")

    try:
        # 1. อ้างอิงถึงเอกสารที่ต้องการลบ
        survey_ref = db.collection('surveys').document(survey_id)
        survey_doc = survey_ref.get()

        if survey_doc.exists:
            # 🔒 ตรวจสอบสิทธิ์: ต้องเป็นเจ้าของเท่านั้นถึงจะลบได้
            if survey_doc.to_dict().get('owner_id') == uid:
                survey_ref.delete()
                messages.success(request, "ลบโปรเจกต์เรียบร้อยแล้ว")
            else:
                messages.error(request, "คุณไม่มีสิทธิ์ลบโปรเจกต์นี้")
        
    except Exception as e:
        print(f"Error deleting project: {e}")
        messages.error(request, "เกิดข้อผิดพลาดในการลบ")

    return redirect("home_page")

def settings_view(request):
    return render(request, 'home/settings.html')

def edit_profile(request):
    return render(request, 'home/edit_profile.html')
