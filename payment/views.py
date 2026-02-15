from django.shortcuts import render

# เพิ่มฟังก์ชันนี้ลงไป
def beta_test_payment(request):
    return render(request, 'payment/beta_test_payment.html')