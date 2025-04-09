# from django.db import models
#
# class Item():
#     name = models.CharField(max_length=255)
#     origin_price = models.DecimalField(max_digits=10, decimal_places=2)
#     current_price = models.DecimalField(max_digits=10, decimal_places=2)
#     stock_quantity = models.IntegerField(default=0)
#     description = models.TextField(blank=True, null=True)
#     def __str__(self):
#         return self.name
#
# class Book(models.Model):
#     author = models.CharField(max_length=255)
#     publisher = models.CharField(max_length=255)
#     isbn = models.CharField(max_length=13)
#     pages = models.IntegerField()
#
#
# class Phone(Item, models.Model):
#     brand = models.CharField(max_length=255)
#     model = models.CharField(max_length=255)
#     ram = models.IntegerField()
#     cpu = models.CharField(max_length=255)
#     def __str__(self):
#         return self.name
#
# class Laptop(Item, models.Model):
#     brand = models.CharField(max_length=255)
#     model = models.CharField(max_length=255)
#     def __str__(self):
#         return self.name

# from django.db import models
# from djongo import models
# from mongoengine import Document, StringField, FloatField
# Models
from mongoengine import Document, StringField, FloatField, DateTimeField, IntField
import datetime

class Item(Document):
    name = StringField(max_length=255, required=True)
    price = FloatField(required=True)
    description = StringField()
    category = StringField(max_length=50)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'items',
        'allow_inheritance': True  # Cho phép kế thừa
    }

    # Đặt tên collection trong MongoDB

    #
    # class Meta:
    #     abstract = True

# Clothes
class Clothes(Item):
    size = StringField(max_length=10, required=True)
    material = StringField(max_length=50, required=True)

# Phone
class Phone(Item):
    brand = StringField(max_length=50, required=True)
    storage = IntField(required=True)

# Laptop
class Laptop(Item):
    brand = StringField(max_length=50, required=True)
    ram = IntField(required=True)

# Book
class Book(Item):
    author = StringField(max_length=255, required=True)
    publisher = StringField(max_length=255, required=True)