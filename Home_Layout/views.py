from django.shortcuts import render, redirect
from core.firebase_config import db # อย่าลืม import db

def home_page(request):
    # 1. เช็คว่ามีคน Login หรือยัง (ดึง uid จาก Session)
    uid = request.session.get("uid")
    if not uid:
        return redirect("login") # ถ้ายังไม่ Login ให้เด้งไปหน้า login

    # 2. ดึงข้อมูล "งานวิจัยของฉัน" จาก Firestore 
    # (ใช้ .where เพื่อกรองเอาเฉพาะงานที่ owner_id ตรงกับคนที่ Login)
    surveys_ref = db.collection('surveys').where('owner_id', '==', uid).stream()
    
    researches = []
    for doc in surveys_ref:
        data = doc.to_dict()
        data['id'] = doc.id # นี่คือ project_id (Document ID ที่ Firebase สร้างให้)
        researches.append(data)

    context = {
        'researches': researches,
        'first_survey': researches[0] if researches else None
    }
    return render(request, 'home/home_preview.html', context)

def settings_view(request):
    return render(request, 'home/settings.html')

def edit_profile(request):
    return render(request, 'home/edit_profile.html')
