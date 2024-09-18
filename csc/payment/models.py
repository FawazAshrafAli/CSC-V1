from django.db import models
from csc_center.models import CscCenter

class Payment(models.Model):
    csc_center = models.ForeignKey(CscCenter, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=100, default='pending')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.unique_token} - {self.status}"

    class Meta:
        ordering = ['-created']


class PaymentHistory(models.Model):
    csc_center = models.ForeignKey(CscCenter, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="Pending")
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"

    class Meta:
        ordering = ['-created']
