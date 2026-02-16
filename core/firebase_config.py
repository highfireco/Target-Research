import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    try:
        # ดึงค่าจาก Environment Variable ของ Render
        firebase_env = os.environ.get('FIREBASE_CREDENTIALS')
        
        if firebase_env:
            cred_dict = json.loads(firebase_env)
            cred = credentials.Certificate(cred_dict)
        else:
            # ใช้ไฟล์ในเครื่อง (Local)
            cred_path = os.getenv('FIREBASE_ACCOUNT_KEY_PATH')
            if not cred_path or not os.path.exists(cred_path):
                return None
            cred = credentials.Certificate(cred_path)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Initialized")

        return firestore.client()
    except Exception as e:
        print(f"🔥 Firebase Error: {e}")
        return None

# 🌟 ประกาศไว้ตรงนี้ ไฟล์อื่นถึงจะ import 'db' ได้
db = initialize_firebase()
