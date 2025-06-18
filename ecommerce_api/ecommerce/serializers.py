from rest_framework import serializers
from .models import Category, Product, Coupon, Address, Wishlist, Cart, CartItem, Order, OrderItem
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Cart.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    image = serializers.ImageField(required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category', 'category_id', 'image', 'created_at']

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_percentage', 'max_discount', 'expiry_date', 'is_active']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'name', 'street', 'city', 'state', 'postal_code', 'country', 'is_default']

    def validate(self, data):
        if data.get('is_default'):
            Address.objects.filter(user=self.context['request'].user, is_default=True).update(is_default=False)
        return data

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_id', 'added_at']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_amount', 'created_at']

    def get_total_amount(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    coupon = CouponSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_amount', 'status', 'items', 'shipping_address', 'billing_address', 'payment_reference', 'coupon', 'discount_applied', 'created_at']

    def validate_status(self, value):
        instance = self.instance
        if instance:
            current_status = instance.status
            invalid_transitions = {
                'delivered': ['pending', 'processing'],
                'completed': ['pending', 'processing', 'failed'],
                'cancelled': ['delivered', 'completed', 'returned', 'refunded'],
                'returned': ['pending', 'processing', 'cancelled', 'refunded'],
                'refunded': ['pending', 'processing', 'cancelled'],
                'failed': ['delivered', 'completed'],
            }
            if value in invalid_transitions and current_status in invalid_transitions[value]:
                raise serializers.ValidationError(f"Cannot change status from {current_status} to {value}")
        return value

class CheckoutSerializer(serializers.Serializer):
    shipping_address_id = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
    billing_address_id = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
    payment_reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
