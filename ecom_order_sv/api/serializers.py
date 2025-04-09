from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'item_id', 'item_name', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['subtotal']

    def validate(self, data):
        # Calculate subtotal
        data['subtotal'] = data['quantity'] * data['unit_price']
        return data


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    payment_info = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'customer_id', 'customer_name', 'customer_email',
            'status', 'total_amount', 'shipping_address',
            'payment_status', 'payment_transaction_id',
            'items', 'payment_info', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_payment_info(self, obj):
        if obj.payment_transaction_id:
            return {
                "status": obj.payment_status,
                "transaction_id": obj.payment_transaction_id
            }
        return None

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order