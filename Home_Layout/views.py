from core.firebase_config import db
from django.shortcuts import render

def home_page(request):
    surveys_ref = db.collection('surveys')
    docs = surveys_ref.stream()
    
    researches = []
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id  # เก็บ Document ID ไว้ใช้เป็น survey_id
        researches.append(data)

    context = {
        'researches': researches,
        # ส่ง survey แรกสุดไปให้ปุ่ม Dashboard ใน Navbar (ถ้ามีข้อมูล)
        'first_survey': researches[0] if researches else None
    }
    return render(request, 'home/home_preview.html', context)

def edit_profile(request):
    return render(request, 'home/edit_profile.html') # เช็คชื่อ Path folder ให้ถูก

def settings_view(request):
    return render(request, 'home/settings.html')

