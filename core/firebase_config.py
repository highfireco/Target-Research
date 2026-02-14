import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    try:
        cred_path = os.getenv('FIREBASE_ACCOUNT_KEY_PATH')
        if not cred_path or not os.path.exists(cred_path):
            raise FileNotFoundError(f"ไม่พบไฟล์ JSON ตาม Path: {cred_path}")

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Firebase: {e}")
        return None

db = initialize_firebase()
