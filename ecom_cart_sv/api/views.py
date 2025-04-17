import logging
import os

import requests
from django.conf import settings
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CartItem
from .serializers import CartItemSerializer

CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL", "http://customer-service.local:30080/api/customers/")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://item-service.local:30080/api/books/")
# CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL", "http://localhost:8001/api/customers/")
# PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8000/api/items/")


logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def _recalculate_cart_total(self, user_id):
        """Calculate cart total and return cart summary"""
        cart_items = CartItem.objects.filter(user_id=user_id)
        total = 0
        items = []

        for item in cart_items:
            try:
                response = requests.get(f"{PRODUCT_SERVICE_URL}{item.product_id}/", timeout=3)
                if response.status_code == 200:
                    product_data = response.json()
                    price = float(product_data.get('price', 0))
                    subtotal = price * item.quantity
                    total += subtotal

                    items.append({
                        'id': item.id,
                        'product_id': item.product_id,
                        'quantity': item.quantity,
                        'price': price,
                        'subtotal': subtotal,
                        'name': product_data.get('name', 'Unknown')
                    })
            except requests.RequestException as e:
                logger.error(f"Failed to fetch product {item.product_id}: {e}")

        return {
            'user_id': user_id,
            'items': items,
            'total_price': total,
            'item_count': len(items)
        }

    @action(detail=False, methods=['get'])
    def cart(self, request):
        """Get complete cart with product details and total"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        cart_data = self._recalculate_cart_total(user_id)
        return Response(cart_data)

    @action(detail=False, methods=['post'])
    def remove_from_cart(self, request):
        """Remove or reduce quantity of a product from the cart"""
        user_id = request.data.get("user_id")
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        remove_all = request.data.get("remove_all", False)

        if not user_id or not product_id:
            return Response({"error": "user_id and product_id are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            return Response({"error": "Quantity must be positive"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = CartItem.objects.get(user_id=user_id, product_id=product_id)

            # Remove the entire item
            if remove_all:
                cart_item.delete()
                return Response(
                    {"message": "Product completely removed from cart"},
                    status=status.HTTP_204_NO_CONTENT
                )

            # Reduce quantity
            if cart_item.quantity > quantity:
                cart_item.quantity -= quantity
                cart_item.save()
                return Response(CartItemSerializer(cart_item).data)
            else:
                # Remove if quantity reaches zero or less
                cart_item.delete()
                return Response(
                    {"message": "Product removed from cart"},
                    status=status.HTTP_204_NO_CONTENT
                )

        except CartItem.DoesNotExist:
            return Response(
                {"error": "Product not found in cart"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        """Add a product to cart or increase quantity if already exists"""
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not user_id or not product_id:
            return Response({'error': 'user_id and product_id are required'},
                            status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            return Response({'error': 'Quantity must be positive'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Optional: Check if product exists
        try:
            response = requests.get(f"{PRODUCT_SERVICE_URL}{product_id}/", timeout=3)
            if response.status_code != 200:
                return Response({'error': 'Product not found'},
                                status=status.HTTP_404_NOT_FOUND)
        except requests.RequestException as e:
            logger.warning(f"Could not verify product {product_id}: {e}")
            # Continue anyway since the check is optional

        # Try to get the existing cart item
        try:
            # Update existing cart item
            cart_item = CartItem.objects.get(user_id=user_id, product_id=product_id)
            cart_item.quantity = models.F('quantity') + quantity
            cart_item.save()
            cart_item.refresh_from_db()  # Refresh to get the new value
            created = False
        except CartItem.DoesNotExist:
            # Create new cart item
            cart_item = CartItem.objects.create(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            created = True

        # Return updated cart data
        cart_data = self._recalculate_cart_total(user_id)
        return Response(cart_data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        """Remove all items from a user's cart"""
        user_id = request.data.get("user_id")

        if not user_id:
            return Response({"error": "user_id is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = CartItem.objects.filter(user_id=user_id).delete()

        return Response({
            "message": f"Cart cleared successfully. {deleted} items removed.",
            "user_id": user_id
        })

    def check_service_exists(self, base_url, object_id):
        """Check if user or product exists"""
        # try:
        #     response = requests.get(f"{base_url}{object_id}/", timeout=3)
        #     return response.status_code == 200
        # except requests.RequestException as e:
        #     logger.error(f"Error checking {base_url}{object_id}: {e}")
        #     # Assume exists if service is down to avoid blocking operations
        #     return True

        return True