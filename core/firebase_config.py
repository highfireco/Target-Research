import os
<<<<<<< HEAD
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

=======
import firebase_admin 
from firebase_admin import credentials, firestore 
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
>>>>>>> origin/project-refactor
load_dotenv()

def initialize_firebase():
    try:
<<<<<<< HEAD
        cred_path = os.getenv('FIREBASE_ACCOUNT_KEY_PATH')
        if not cred_path or not os.path.exists(cred_path):
            raise FileNotFoundError(f"ไม่พบไฟล์ JSON ตาม Path: {cred_path}")

=======
        # ดึง Path ของไฟล์ JSON จาก .env
        cred_path = os.getenv('FIREBASE_ACCOUNT_KEY_PATH')
        
        # ตรวจสอบว่ามีไฟล์อยู่จริงหรือไม่
        if not cred_path or not os.path.exists(cred_path):
            raise FileNotFoundError(f"ไม่พบไฟล์ JSON ตาม Path ที่ระบุ: {cred_path}")

        # เริ่มต้น Firebase Admin SDK
>>>>>>> origin/project-refactor
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Firebase: {e}")
        return None

<<<<<<< HEAD
db = initialize_firebase()
=======
# สร้างตัวแปร db ไว้ใช้งาน
db = initialize_firebase()
>>>>>>> origin/project-refactor
