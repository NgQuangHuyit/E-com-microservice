# api/models.py
from django.db import models


class UserInteraction(models.Model):
    user_id = models.IntegerField(db_index=True)
    product_id = models.CharField(max_length=100, db_index=True)  #
    interaction_type = models.CharField(max_length=20, choices=[
        ('view', 'View'),
        ('cart', 'Add to Cart'),
        ('purchase', 'Purchase'),
    ])
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['product_id', 'timestamp']),
        ]


class ProductFeature(models.Model):
    product_id = models.CharField(max_length=100, unique=True)
    features = models.JSONField()  # Store category, tags, etc.
    updated_at = models.DateTimeField(auto_now=True)