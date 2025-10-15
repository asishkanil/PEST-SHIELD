from django.contrib import admin
from .models import Pesticide, Cart, Order, OrderConfirmation, OrderItem, CartItem

@admin.register(Pesticide)
class PesticideAdmin(admin.ModelAdmin):
    list_display = ("pesticide_name", "pest_name", "price", "quantity_available")
    search_fields = ("pesticide_name", "pest_name")
    list_filter = ("pest_name",)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "pesticide", "quantity")
    search_fields = ("user__username", "pesticide__pesticide_name")
    list_filter = ("user",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "pesticide", "quantity", "total_price", "order_date", "status")
    search_fields = ("user__username", "pesticide__pesticide_name")
    list_filter = ("status", "order_date")

@admin.register(OrderConfirmation)
class OrderConfirmationAdmin(admin.ModelAdmin):
    list_display = ("item", "pest_name", "price", "quantity", "status")
    search_fields = ("item", "pest_name")
    list_filter = ("status",)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "pesticide", "quantity")
    search_fields = ("order__id", "pesticide__pesticide_name")

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "session_key")
    search_fields = ("product__pesticide_name", "session_key")
