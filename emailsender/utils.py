from django.core.mail import send_mail
from django.conf import settings

def send_invite(email):
    subject = "You're Invited!"
    message = "You have been invited to join our platform. Welcome!"
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
