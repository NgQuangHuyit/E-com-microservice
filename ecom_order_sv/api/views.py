from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
import requests
from django.conf import settings
from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        # Get user_id instead of cart_id
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get cart items from cart service using user_id
        try:
            cart_response = requests.get(f"{settings.CART_SERVICE_URL}/api/cart-items/cart/?user_id={user_id}")
            cart_response.raise_for_status()
            cart_data = cart_response.json()
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to fetch cart: {str(e)}"},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
        if cart_data.get('item_count', 0) == 0:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        # Get customer details from customer service
        customer_id = user_id  # Assuming user_id is the same as customer_id
        try:
            customer_response = requests.get(f"{settings.CUSTOMER_SERVICE_URL}/api/customers/{customer_id}/")
            customer_response.raise_for_status()
            customer_data = customer_response.json()
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to fetch customer: {str(e)}"},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Prepare order data
        order_data = {
            "customer_id": customer_id,
            "customer_name": customer_data.get('name'),
            "customer_email": customer_data.get('email'),
            "shipping_address": request.data.get('shipping_address'),
            "total_amount": cart_data.get('total_price'),  # Adjust based on your cart response format
            "status": "awaiting_payment",
            "items": []
        }

        # Prepare items data
        for cart_item in cart_data.get('items', []):
            product_id = cart_item.get('product_id')
            quantity = cart_item.get('quantity')
            price = cart_item.get('price', 0)  # Your cart might already include price info

            order_data["items"].append({
                "item_id": product_id,
                "item_name": cart_item.get('name', 'Unknown Product'),  # Adjust based on your data
                "quantity": quantity,
                "unit_price": price,
                "subtotal": quantity * float(price)
            })

        # Create order with serializer
        serializer = self.get_serializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Clear the cart after order creation
        try:
            requests.post(f"{settings.CART_SERVICE_URL}/api/cart-items/clear_cart/",
                          json={"user_id": user_id})
        except requests.exceptions.RequestException:
            pass

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        order = self.get_object()
        payment_method = request.data.get('payment_method')

        if not payment_method:
            return Response({"error": "Payment method is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare payment request data
        payment_data = {
            "order_id": str(order.id),
            "customer_id": order.customer_id,
            "payment_method": payment_method,
            "amount": str(order.total_amount),
            "currency": "USD",  # Could be configurable
        }

        # Call payment service to process payment
        try:
            payment_response = requests.post(
                f"{settings.PAYMENT_SERVICE_URL}/api/payments/",
                json=payment_data,
                timeout=5  # Adding timeout for better error handling
            )
            payment_response.raise_for_status()
            payment_result = payment_response.json()

            # Update order with payment information
            order.payment_status = payment_result.get('status')
            order.payment_transaction_id = payment_result.get('transaction_id')

            if payment_result.get('status') == 'completed':
                order.status = 'processing'

            order.save()

            return Response(payment_result)

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Payment service error: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @action(detail=True, methods=['post'])
    def update_payment_status(self, request, pk=None):
        """Webhook endpoint for payment service to update order status"""
        order = self.get_object()
        status = request.data.get('status')
        transaction_id = request.data.get('transaction_id')

        if status == 'completed':
            order.status = 'processing'
            order.payment_status = 'completed'
        elif status == 'refunded':
            order.status = 'cancelled'
            order.payment_status = 'refunded'
        elif status == 'failed':
            order.payment_status = 'failed'

        if transaction_id:
            order.payment_transaction_id = transaction_id

        order.save()

        return Response({"status": "updated"})

    @action(detail=False, methods=['get'])
    def customer_orders(self, request):
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        orders = Order.objects.filter(customer_id=customer_id)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint for Kubernetes liveness and readiness probes
    """
    return Response({"status": "healthy"})