from django.shortcuts import render

def project_summary(request):
    return render(request, "payment/project_summary.html")

def payment_page(request):
    return render(request, "payment/payment.html")
