from .firebase import db
from datetime import datetime

def create_notification(user_id, message, type):
    notification_ref = db.collection("notifications").document()

    notification_ref.set({
        "user_id": user_id,
        "message": message,
        "type": type,
        "read": False,
        "created_at": datetime.utcnow()
    })

    return notification_ref.id
