import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# 🛑 ท่าไม้ตาย: เช็คว่ากำลังรันคำสั่ง collectstatic อยู่หรือไม่?
# ถ้าใช่ ให้ข้ามการโหลด Firebase ไปเลย (เพราะ collectstatic ไม่ต้องใช้ Database)
if 'collectstatic' in sys.argv:
    print("--- 🚧 Building Mode: Skipping Firebase Initialization ---")
    db = None
else:
    # --- ส่วนทำงานปกติ (Runtime) ---
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        # สร้างฟังก์ชัน get_db แบบ Lazy (เรียกใช้เมื่อจำเป็นจริงๆ)
        def _get_active_db():
            if not firebase_admin._apps:
                firebase_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
                cred = None
                
                if firebase_json:
                    cred_dict = json.loads(firebase_json)
                    cred = credentials.Certificate(cred_dict)
                else:
                    cred_path = os.getenv('FIREBASE_ACCOUNT_KEY_PATH')
                    if cred_path and os.path.exists(cred_path):
                        cred = credentials.Certificate(cred_path)
                
                if cred:
                    firebase_admin.initialize_app(cred)
            
            return firestore.client()

        # Class หลอกๆ เพื่อให้ Django เรียกใช้ db ได้โดยไม่ Error ตอน import
        class LazyDB:
            _client = None
            
            def __getattr__(self, name):
                if self._client is None:
                    self._client = _get_active_db()
                return getattr(self._client, name)

        db = LazyDB()
        print("--- ✅ Firebase Config Loaded Successfully ---")

    except Exception as e:
        print(f"--- ⚠️ Warning: Firebase failed to load: {e} ---")
        db = None