from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'status', 'total_amount', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status']
    search_fields = ['customer_name', 'customer_email']
    inlines = [OrderItemInline]