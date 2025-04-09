from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
# router.register(r'items', ItemViewSet)
router.register(r'items', ItemsViewSet, basename='items')
router.register(r'clothes', ClothesViewSet, basename='clothes')
router.register(r'phones', PhoneViewSet, basename='phones')
router.register(r'laptops', LaptopViewSet, basename='laptops')
router.register(r'books', BookViewSet, basename='books')

urlpatterns = [
    path('', include(router.urls)),
]

