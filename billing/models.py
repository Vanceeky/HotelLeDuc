from django.db import models
from booking.models import Booking
from restaurant.models import Order, OrderItem

# Create your models here.

class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    issued_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Invoice for Order #{self.order.pk} - Issued at: {self.issued_at} - Total Amount: ₱{self.total_amount}"

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
