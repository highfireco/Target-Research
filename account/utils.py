import random
from django.core.mail import send_mail
from django.conf import settings

def generate_pin():
    return str(random.randint(100000, 999999))

def send_pin_email(email, pin):
    subject = "Your verification code"
    message = f"Your verification code is: {pin}"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])