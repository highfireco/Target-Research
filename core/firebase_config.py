import os
import json
from dotenv import load_dotenv

load_dotenv()

# สร้างตัวแปร Global ไว้เก็บค่า
_db = None

def get_db():
    global _db
    
    if _db is not None:
        return _db

    try:
        # 🌟 ย้ายการ Import มาไว้ข้างในฟังก์ชัน (Lazy Import)
        # เพื่อป้องกัน Error '_cffi_backend' ตอน Build (collectstatic)
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # ตรวจสอบว่ามี App รันอยู่หรือยัง
        if not firebase_admin._apps:
            firebase_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
            cred = None
            
            if firebase_json:
                print("--- Vercel Mode: Loading from Env ---")
                cred_dict = json.loads(firebase_json)
                cred = credentials.Certificate(cred_dict)
            else:
                cred_path = os.getenv('FIREBASE_ACCOUNT_KEY_PATH')
                if not cred_path or not os.path.exists(cred_path):
                    # ถ้าหาไฟล์ไม่เจอ (เช่นตอน Build บน Server) ให้คืนค่า None ไปก่อน
                    print("Warning: Firebase config not found.")
                    return None
                cred = credentials.Certificate(cred_path)

            firebase_admin.initialize_app(cred)
            
        _db = firestore.client()
        return _db
        
    except Exception as e:
        print(f"Error connecting to Firebase: {e}")
        return None

# Class สำหรับหลอก Django ว่ามีตัวแปร db อยู่จริง แต่ยังไม่ทำงานจนกว่าจะถูกเรียกใช้
class LazyDB:
    def __getattr__(self, name):
        db_instance = get_db()
        if db_instance is None:
            raise Exception("Firebase Database is not connected yet.")
        return getattr(db_instance, name)

# ตัวแปรนี้จะถูก import ไปใช้ที่อื่น แต่จะยังไม่ connect database ทันที
db = LazyDB()