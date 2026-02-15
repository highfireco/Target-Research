class UserTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ดึงเส้นทาง URL ที่กำลังเข้า
        path = request.path
        
        # กรองไม่ให้มัน Print พวกไฟล์รูปภาพ หรือ CSS ออกมาให้รกจอ
        if not path.startswith('/static/') and not path.startswith('/admin/'):
            
            # ดึง UID จาก Session ที่เราบันทึกไว้ตอน Login
            uid = request.session.get('uid')
            
            if uid:
                print(f"👀 [TRACKING] User ID: {uid} | กำลังเข้าหน้า: {path}")
            else:
                print(f"👀 [TRACKING] Guest (ยังไม่ Login) | กำลังเข้าหน้า: {path}")

        # ปล่อยให้ระบบทำงานต่อไป
        response = self.get_response(request)
        return response