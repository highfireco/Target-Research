from django.http import HttpResponse
from django.shortcuts import render
from core.firebase_config import db

def dashboard_view(request):
    return render(request, 'test.html')
# Create your views here.


def verify_firebase(request):
    if db is None:
        return HttpResponse("❌ เชื่อมต่อ Firebase ไม่สำเร็จ: กรุณาตรวจสอบไฟล์ .env หรือ Path ของไฟล์ JSON")

    try:
        # ทดลองดึงข้อมูลจาก Collection ใดก็ได้ (เช่น 'test_connection')
        # หากยังไม่มี Collection นี้ใน Firebase ระบบจะไม่ Error แต่จะคืนค่าว่าง
        doc_ref = db.collection('system_check').document('status')
        doc = doc_ref.get()

        if doc.exists:
            status_data = doc.to_dict()
            return HttpResponse(f"✅ เชื่อมต่อสำเร็จ! ข้อมูลในระบบ: {status_data}")
        else:
            return HttpResponse("✅ เชื่อมต่อสำเร็จ! (แต่ยังไม่มีข้อมูลใน Collection 'system_check')")
            
    except Exception as e:
        return HttpResponse(f"❌ เกิดข้อผิดพลาดขณะดึงข้อมูล: {e}")