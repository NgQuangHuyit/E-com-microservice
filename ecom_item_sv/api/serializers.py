from rest_framework import serializers
from .models import *


# class ItemSerializer(serializers.Serializer):
#     class Meta:
#         fields = '__all__'

# class ItemSerializer(serializers.Serializer):
#     class Meta:
#         model = Item
#         fields = '__all__'
#
# class ClothesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Clothes
#         fields = '__all__'
#
# class PhoneSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Phone
#         fields = '__all__'
#
# class LaptopSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Laptop
#         fields = '__all__'
#
# class BookSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Book
#         fields = '__all__'
#
# class ClothesSerializer(ItemSerializer):
#     size = serializers.CharField()
#     material = serializers.CharField()
#     color = serializers.CharField()
#
#     class Meta:
#         model = Clothes
#         fields = '__all__'

class ItemSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)  # MongoDB ObjectId
    name = serializers.CharField()
    price = serializers.FloatField()
    description = serializers.CharField()
    category = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

class ClothesSerializer(ItemSerializer):
    size = serializers.CharField()
    material = serializers.CharField()

    def create(self, validated_data):
        return Clothes(**validated_data).save()

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

class PhoneSerializer(ItemSerializer):
    brand = serializers.CharField()
    storage = serializers.IntegerField()

    def create(self, validated_data):
        return Phone(**validated_data).save()

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

class LaptopSerializer(ItemSerializer):
    brand = serializers.CharField()
    ram = serializers.IntegerField()

    def create(self, validated_data):
        return Laptop(**validated_data).save()

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

class BookSerializer(ItemSerializer):
    author = serializers.CharField()
    publisher = serializers.CharField()

    def create(self, validated_data):
        return Book(**validated_data).save()

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance