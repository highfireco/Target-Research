import os
import json
import firebase_admin 
from firebase_admin import credentials, firestore 
from dotenv import load_dotenv

#โหลดค่าจากไฟล์ .env (สำหรับรันในเครื่อง)
load_dotenv()

def initialize_firebase():
    try:
        # 🌟 1. ตรวจสอบว่ามีตัวแปร FIREBASE_CREDENTIALS (บน Render) หรือไม่
        firebase_env = os.environ.get('FIREBASE_CREDENTIALS')

        if firebase_env:
            # --- กรณีรันบน Render: ดึงข้อมูล JSON จาก Environment Variable ---
            print("--- DEBUG: Using Firebase from Environment Variable (Render) ---")
            cred_dict = json.loads(firebase_env)
            cred = credentials.Certificate(cred_dict)
        else:
            # --- กรณีรันในเครื่อง: ดึงจาก Path ไฟล์ JSON ปกติ ---
            cred_path = os.getenv('FIREBASE_ACCOUNT_KEY_PATH')
            print(f"--- DEBUG: Current Firebase Path: {cred_path} ---")

            if not cred_path or not os.path.exists(cred_path):
                raise FileNotFoundError(f"ไม่พบไฟล์ JSON หรือตัวแปรสภาพแวดล้อมสำหรับ Firebase")

            cred = credentials.Certificate(cred_path)

        # 🌟 2. นี่คือจุดที่ทำการ initialize_app (เปิดเครื่อง)
        if not firebase_admin._apps:
            app = firebase_admin.initialize_app(cred)  # <--- บรรทัดสำคัญที่ระบบแจ้งเตือนครับ
            print(f"--- DEBUG: Connected to Project ID: {app.project_id} ---")

        return firestore.client()
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Firebase: {e}")
        return None

#สร้างตัวแปร db ไว้ใช้งาน
db = initialize_firebase()