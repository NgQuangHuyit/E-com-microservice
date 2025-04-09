from django.db import models

# Create your models here.

class Customer(models.Model):
    CUSTOMER_TYPES = [
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]


    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    customer_type = models.CharField(max_length=10, choices=CUSTOMER_TYPES, default='silver')
    rewards_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.customer_type})"

class Address(models.Model):
    customer = models.ForeignKey(Customer, related_name='addresses', on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=10)
    receiver_phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}"
