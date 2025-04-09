from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Customer, Address
from .serializers import CustomerSerializer, AddressSerializer
from .models import Customer, Address

# Create your views here.
class CustomerListCreateAPIView(APIView):
    """
    API để lấy danh sách khách hàng hoặc tạo mới khách hàng.
    """
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

class CustomerDetailAPIView(APIView):
    """
    API để lấy, cập nhật hoặc xóa một khách hàng cụ thể.
    """
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def put(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CustomerRegisterAPIView(APIView):
    """
    API để khách hàng đăng ký tài khoản.
    """
    def post(self, request):
        data = request.data.copy()

        if (data.get('phone') is None) and (data.get('email') is None):
            return Response({'error': 'Phone or email is required'}, status=status.HTTP_400_BAD_REQUEST)
        if (data.get('phone') is not None and Customer.objects.filter(phone=data.get('phone')).exists()) or (Customer.objects.filter(email=data.get('email')).exists()):
            return Response({'error': 'Phone or email is already used'}, status=status.HTTP_400_BAD_REQUEST)
        if (data.get('email') is not None and Customer.objects.filter(email=data.get('email')).exists()) or (Customer.objects.filter(phone=data.get('phone')).exists()):
            return Response({'error': 'Phone or email is already used'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CustomerSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreateAPIView(APIView):
    """
    API để lấy danh sách địa chỉ của khách hàng hoặc thêm địa chỉ mới.
    """
    def get(self, request):
        addresses = Address.objects.all()
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddressDetailAPIView(APIView):
    """
    API để lấy, cập nhật hoặc xóa một địa chỉ cụ thể.
    """
    def get(self, request, pk):
        address = get_object_or_404(Address, pk=pk)
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def put(self, request, pk):
        address = get_object_or_404(Address, pk=pk)
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        address = get_object_or_404(Address, pk=pk)
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CustomerAddressAPIView(APIView):
    """
    API để tạo mới địa chỉ cho một khách hàng.
    """
    def post(self, request, customerID):
        customer = get_object_or_404(Customer, pk=customerID)
        data = request.data.copy()
        data['customer'] = customer.id
        serializer = AddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, customerID):
        customer = get_object_or_404(Customer, pk=customerID)
        addresses = Address.objects.filter(customer=customer)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

@api_view(http_method_names=['POST'])
def get_customers(request):
    customer = Customer.objects.create(
        name=request.data.get('name'),
        email=request.data.get('email'),
        phone=request.data.get('phone'),
        customer_type=request.data.get('customer_type'),
        rewards_points=request.data.get('rewards_points')
    )