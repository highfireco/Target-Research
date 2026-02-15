import os
import firebase_admin 
import json
from firebase_admin import credentials, firestore 
from dotenv import load_dotenv

load_dotenv()

# สร้างตัวแปร Global ไว้เก็บค่า
_db = None

def get_db():
    global _db
    
    # ถ้าเคยเชื่อมต่อแล้ว ให้ส่งตัวเดิมกลับไปเลย (ไม่ต้องต่อใหม่)
    if _db is not None:
        return _db

    try:
        # --- (โค้ดเชื่อมต่อเดิมของคุณ) ---
        firebase_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
        cred = None
        
        if firebase_json:
            print("--- Vercel Mode: Loading from Env ---")
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
        else:
            cred_path = os.getenv('FIREBASE_ACCOUNT_KEY_PATH')
            if not cred_path or not os.path.exists(cred_path):
                 # กรณีรัน collectstatic บน Server อาจจะไม่มีไฟล์ ก็ให้ข้ามไปก่อน
                print("Warning: Firebase config not found.")
                return None
            cred = credentials.Certificate(cred_path)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            
        _db = firestore.client()
        return _db
        
    except Exception as e:
        print(f"Error connecting to Firebase: {e}")
        return None

# 🌟 เปลี่ยนจาก db = initialize_firebase() เป็นตัวนี้แทน:
# ใช้ Lazy Object เพื่อให้ Django ไม่พังตอน Load settings
class LazyDB:
    def __getattr__(self, name):
        return getattr(get_db(), name)

db = LazyDB()