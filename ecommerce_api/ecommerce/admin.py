from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Category, Product, Coupon, Address, Wishlist, Cart, CartItem, Order, OrderItem
admin.site.site_header = "eCommerce"
admin.site.site_title = "eCommerce Portal"
admin.site.index_title = "Welcome to the eCommerce"
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'city', 'country', 'is_default')
    search_fields = ('user__username', 'name', 'city', 'country')
    ordering = ('user',)
    raw_id_fields = ('user',)
    list_per_page = 10

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('added_at',)
    ordering = ('added_at',)
    raw_id_fields = ('user', 'product')
    list_per_page = 10

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)
    ordering = ('created_at',)
    raw_id_fields = ('user',)
    list_per_page = 10

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__user__username', 'product__name')
    ordering = ('cart',)
    raw_id_fields = ('cart', 'product')
    list_per_page = 10

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    search_fields = ('user__username', 'payment_reference')
    ordering = ('-created_at',)
    raw_id_fields = ('user', 'coupon')
    list_editable = ('status',)
    list_per_page = 10

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')
    ordering = ('order',)
    raw_id_fields = ('order', 'product')
    list_per_page = 10
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)
    list_per_page = 10
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    raw_id_fields = ('category',)
    list_per_page = 10