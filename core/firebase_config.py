import os
import firebase_admin 
from firebase_admin import credentials, firestore 
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

def initialize_firebase():
    try:
        # ดึง Path ของไฟล์ JSON จาก .env
        cred_path = os.getenv('FIREBASE_ACCOUNT_KEY_PATH')
        
        # DEBUG: พิมพ์พาธที่ระบบกำลังเรียกใช้ออกมาดูใน Terminal
        print(f"--- DEBUG: Current Firebase Path: {cred_path} ---")

        if not cred_path or not os.path.exists(cred_path):
            raise FileNotFoundError(f"ไม่พบไฟล์ JSON ตาม Path ที่ระบุ: {cred_path}")

        # เริ่มต้น Firebase Admin SDK
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            # เริ่มต้น Firebase และตรวจสอบ Project ID ทันที
            app = firebase_admin.initialize_app(cred)
            print(f"--- DEBUG: Connected to Project ID: {app.project_id} ---")

        return firestore.client()
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Firebase: {e}")
        return None

# สร้างตัวแปร db ไว้ใช้งาน
db = initialize_firebase()
