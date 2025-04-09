from django.db import models
from django.utils import timezone


class CartItem(models.Model):
    user_id = models.CharField(max_length=100)
    product_id = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_id', 'product_id')

    def __str__(self):
        return f"CartItem: {self.user_id} - {self.product_id} ({self.quantity})"