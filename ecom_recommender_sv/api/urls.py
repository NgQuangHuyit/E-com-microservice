# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecommendationViewSet, InteractionViewSet, health_check, ProductFeatureViewSet

router = DefaultRouter()
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')
router.register(r'interactions', InteractionViewSet)
router.register(r"product_features", ProductFeatureViewSet, basename='product_feature')
urlpatterns = [
    path('', include(router.urls)),
    path('health/', health_check, name='health_check'),
]