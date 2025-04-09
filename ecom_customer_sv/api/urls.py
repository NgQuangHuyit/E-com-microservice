from django.urls import path
from .views import (
    CustomerListCreateAPIView, CustomerDetailAPIView,
    AddressListCreateAPIView, AddressDetailAPIView, CustomerRegisterAPIView, CustomerAddressAPIView
)

urlpatterns = [
    path('customers/', CustomerListCreateAPIView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerDetailAPIView.as_view(), name='customer-detail'),
    path('customers/<int:customerID>/addresses/', CustomerAddressAPIView.as_view(), name='customer-address-list'),
    path('addresses/', AddressListCreateAPIView.as_view(), name='address-list-create'),
    path('addresses/<int:pk>/', AddressDetailAPIView.as_view(), name='address-detail'),
    path("register/", CustomerRegisterAPIView.as_view(), name="customer-register"),
]
