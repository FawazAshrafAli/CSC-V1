from celery import shared_task


@shared_task
def check_validity():
    print("Working")

# from django.utils import timezone
# from datetime import timedelta
# from .models import CscCenter

# one_year_ago = timezone.now() - timedelta(days=365)
    # old_centers = CscCenter.objects.filter(created__lt=one_year_ago)