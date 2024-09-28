from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import CscCenter

def send_expired_notification_mail(center):
    subject = 'Your  Csc Center Account is Expired'
    from_email = 'w3digitalpmna@gmail.com'
    to_email = [center.email]

    html_content = render_to_string('email_templates/csc_expired.html', {
        'owner_name': center.owner,
        'expiration_date': timezone.now().date(),
        'support_email': from_email
    })

    email = EmailMultiAlternatives(subject, '', from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    
    # Send email
    email.send()
 

# Using shared_task to register this task with Django's Celery instance
@shared_task
def send_test_email():
    subject = 'Hello from Django'
    message = 'This is a test email from Django.'
    recipient_list = ['w3digitalpmna@gmail.com']
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # From email
        recipient_list,
        fail_silently=False,
    )

@shared_task
def check_validty():
    this_day_last_year = timezone.now().date() - timedelta(days = 365)
    # expired_csc_centers = CscCenter.objects.filter(email = "w3digitalpmna@gmail.com", created__lt = this_day_last_year, is_active = True)
    expired_csc_centers = CscCenter.objects.filter(email = "w3digitalpmna@gmail.com", created__lt = this_day_last_year)
    
    for csc_center in expired_csc_centers:
        csc_center.is_active = False
        csc_center.save()
        send_expired_notification_mail(csc_center)