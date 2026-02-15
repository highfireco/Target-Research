import os
import firebase_admin 
import json
from firebase_admin import credentials, firestore 
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env (สำหรับรันในเครื่อง)
load_dotenv()

def initialize_firebase():
    try:
        # ---------------------------------------------------------
        # 1. สำหรับ Vercel (Production): อ่านจากตัวแปร Environment โดยตรง
        # ---------------------------------------------------------
        # เราจะตั้งชื่อตัวแปรใหม่ใน Vercel ว่า 'FIREBASE_CREDENTIALS_JSON'
        firebase_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
        
<<<<<<< HEAD
        cred = None
        
        if firebase_json:
            print("--- DEBUG: Found FIREBASE_CREDENTIALS_JSON in Env (Vercel Mode) ---")
            # แปลง String (JSON) ให้เป็น Dictionary เพื่อใช้งานทันที
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
            
        # ---------------------------------------------------------
        # 2. สำหรับ Local (Development): อ่านจากไฟล์ Path เหมือนเดิม
        # ---------------------------------------------------------
        else:
            cred_path = os.getenv('FIREBASE_ACCOUNT_KEY_PATH')
            print(f"--- DEBUG: Current Firebase Path: {cred_path} (Local Mode) ---")

            if not cred_path or not os.path.exists(cred_path):
                # ถ้าหาไม่เจอทั้งคู่ ให้แจ้ง Error
                raise FileNotFoundError(f"ไม่พบไฟล์ JSON หรือตัวแปร Environment สำหรับ Firebase")
=======
        # DEBUG: พิมพ์พาธที่ระบบกำลังเรียกใช้ออกมาดูใน Terminal
        print(f"--- DEBUG: Current Firebase Path: {cred_path} ---")

        if not cred_path or not os.path.exists(cred_path):
            raise FileNotFoundError(f"ไม่พบไฟล์ JSON ตาม Path ที่ระบุ: {cred_path}")
>>>>>>> 416e3c37a52b50cd36b21f3c93479de520980dee

            cred = credentials.Certificate(cred_path)
<<<<<<< HEAD

        # ---------------------------------------------------------
        # เริ่มต้น Firebase Admin SDK
        # ---------------------------------------------------------
        if not firebase_admin._apps:
            # เริ่มต้น Firebase
=======
            # เริ่มต้น Firebase และตรวจสอบ Project ID ทันที
>>>>>>> 416e3c37a52b50cd36b21f3c93479de520980dee
            app = firebase_admin.initialize_app(cred)
            print(f"--- DEBUG: Connected to Project ID: {app.project_id} ---")

        return firestore.client()
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Firebase: {e}")
        return None

# สร้างตัวแปร db ไว้ใช้งาน
db = initialize_firebase()
