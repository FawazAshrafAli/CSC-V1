from django.core.mail import send_mail, BadHeaderError
from celery import shared_task
from celery.utils.log import get_task_logger

# logger = get_task_logger(__name__)



# @shared_task
# def send_otp_email(email, otp):
#     subject = 'OTP for setting password'
#     message = f'Your OTP code is {otp}. It is valid for the next 10 minutes.'
#     from_email = 'w3digitalpmna@gmail.com'
#     receipient_list = [email]

#     # send_mail(subject, message, from_email, receipient_list)

#     try:
#         send_mail(subject, message, from_email, receipient_list)
#         logger.info("Email sent successfully to %s", email)
#     except BadHeaderError:
#         logger.error("Invalid header found for email: %s", email)
#     except Exception as e:
#         logger.error("An error occurred while sending email: %s", str(e))
