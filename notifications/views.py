from django.shortcuts import render

def notification_home(request):
    return render(request, "notifications/notification_home.html")


def survey_notification(request):
    return render(request, "notifications/survey_notification.html")

def project_progress_notification(request):
    return render(request, "notifications/project_progress_notification.html")

def payment_notification(request):
    return render(request, "notifications/payment_notification.html")

