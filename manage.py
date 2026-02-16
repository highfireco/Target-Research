import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') # หรือชื่อโฟลเดอร์ settings ของคุณ

    # 🛑 แผนนิวเคลียร์: หลอกระบบตอนสร้างไฟล์ (Build)
    # ถ้ากำลังรันคำสั่ง 'collectstatic' ให้สร้าง "ตัวปลอม" (Mock) มาทำงานแทน
    # วิธีนี้จะทำให้ Django ไม่ไปแตะต้อง Library ที่มีปัญหาเลย
    if 'collectstatic' in sys.argv:
        from unittest.mock import MagicMock
        sys.modules['firebase_admin'] = MagicMock()
        sys.modules['firebase_admin.credentials'] = MagicMock()
        sys.modules['firebase_admin.firestore'] = MagicMock()
        sys.modules['google'] = MagicMock()
        sys.modules['google.cloud'] = MagicMock()
        sys.modules['google.oauth2'] = MagicMock()
        print("--- 🚧 Mocking Firebase modules for build process ---")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()