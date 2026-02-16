def initialize_firebase():
    try:
        # 🌟 เพิ่มส่วนนี้เพื่อรองรับ Render
        firebase_env = os.environ.get('FIREBASE_CREDENTIALS')
        
        if firebase_env:
            import json
            cred_dict = json.loads(firebase_env)
            cred = credentials.Certificate(cred_dict)
        else:
            # กรณีรันในเครื่อง (Local)
            cred_path = os.getenv('FIREBASE_ACCOUNT_KEY_PATH')
            cred = credentials.Certificate(cred_path)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"🔥 Firebase Error: {e}")
        return None
