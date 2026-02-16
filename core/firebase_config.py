import os
import json
import firebase_admin 
from firebase_admin import credentials, firestore 
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env (สำหรับรันในเครื่อง)
load_dotenv()

def initialize_firebase():
    try:
        # 🌟 ตรวจสอบค่าจาก Render
        firebase_env = os.environ.get('FIREBASE_CREDENTIALS')
        
        if firebase_env:
            # --- บน Render ---
            cred_dict = json.loads(firebase_env)
            cred = credentials.Certificate(cred_dict)
        else:
            # --- ในเครื่องคอมพิวเตอร์ ---
            cred_path = os.getenv('FIREBASE_ACCOUNT_KEY_PATH')
            if not cred_path or not os.path.exists(cred_path):
                print("⚠️ Warning: Firebase credentials not found.")
                return None
            cred = credentials.Certificate(cred_path)

        # เริ่มต้น Firebase
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Initialized Successfully")

        return firestore.client()
    except Exception as e:
        print(f"🔥 Firebase Error: {e}")
        return None

# 🌟 ย้ายมาไว้นอกฟังก์ชันตรงนี้ เพื่อให้ไฟล์อื่น Import 'db' ไปใช้ได้
db = initialize_firebase()
