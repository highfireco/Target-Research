import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
import os

if not firebase_admin._apps:
    cred_path = os.path.join(
        settings.BASE_DIR,
        "..",
        "target-research-6b556-firebase-adminsdk-fbsvc-cb6ec548bb.json"
    )
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()
