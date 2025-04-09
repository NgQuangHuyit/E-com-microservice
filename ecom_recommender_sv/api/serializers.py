# api/serializers.py
from rest_framework import serializers
from .models import UserInteraction, ProductFeature


class UserInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteraction
        fields = '__all__'


class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = '__all__'


class RecommendationRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    limit = serializers.IntegerField(default=5)