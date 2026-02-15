import os
import firebase_admin
from firebase_admin import credentials, auth

# หา BASE_DIR แบบปลอดภัย
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# สร้าง path ไป firebase_key.json
cred_path = os.path.join(BASE_DIR, "firebase_key.json")

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase connected successfully")
    except Exception as e:
        print("Firebase connection error:", e)


def verify_firebase_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception:
        return None
