from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import ScopedRateThrottle
from .models import Category, Product, Coupon, Address, Wishlist, Cart, CartItem, Order, OrderItem
from .serializers import (
    UserSerializer, CategorySerializer, ProductSerializer, CouponSerializer,
    AddressSerializer, WishlistSerializer, CartSerializer, CartItemSerializer,
    OrderSerializer, OrderItemSerializer, CheckoutSerializer
)
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User

import random  # For simulating payment failure

class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'sensitive'

class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'sensitive'

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = get_object_or_404(User, username=username)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class WishlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WishlistDeleteView(generics.DestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CategorySearchView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    pagination_class = None

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    pagination_class = None

class ProductFilterByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        category_id = self.request.query_params.get('category_id')
        if category_id:
            return Product.objects.filter(category_id=category_id)
        return Product.objects.all()

class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Cart, user=self.request.user)

class CartItemAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if quantity < 1:
            return Response({'error': 'Quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product, id=product_id)
        if product.stock < quantity:
            return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            if product.stock < cart_item.quantity + quantity:
                return Response({'error': 'Insufficient stock for additional quantity'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity += quantity
            cart_item.save()
        
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

class CartItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        action = request.data.get('action')

        if action == 'increment':
            if cart_item.product.stock <= cart_item.quantity:
                return Response({'error': 'Cannot increment, out of stock'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity += 1
        elif action == 'decrement':
            if cart_item.quantity <= 1:
                return Response({'error': 'Cannot decrement below 1'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity -= 1
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.save()
        return Response(CartItemSerializer(cart_item).data)

class CartItemDeleteView(generics.DestroyAPIView):
    queryset = CartItem.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

class CartClearView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared successfully'}, status=status.HTTP_204_NO_CONTENT)

class CheckoutPreviewView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'checkout'

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        coupon_code = request.data.get('coupon_code')
        coupon = None
        discount_applied = 0
        if coupon_code:
            coupon = get_object_or_404(Coupon, code=coupon_code)
            if not coupon.is_valid():
                return Response({'error': 'Invalid or expired coupon'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CartSerializer(cart)
        data = serializer.data
        total_amount = data['total_amount']
        if coupon:
            discount_applied = total_amount * (coupon.discount_percentage / 100)
            if coupon.max_discount and discount_applied > coupon.max_discount:
                discount_applied = coupon.max_discount
            total_amount -= discount_applied

        data['coupon_code'] = coupon_code if coupon else None
        data['discount_applied'] = discount_applied
        data['tax'] = total_amount * 0.1
        data['shipping_cost'] = 10.00
        data['grand_total'] = total_amount + data['tax'] + data['shipping_cost']
        return Response(data)

class CheckoutValidateView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'checkout'

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        out_of_stock_items = []
        for item in cart.items.all():
            if item.product.stock < item.quantity:
                out_of_stock_items.append({
                    'product': item.product.name,
                    'available_stock': item.product.stock,
                    'requested_quantity': item.quantity
                })

        if out_of_stock_items:
            return Response({
                'error': 'Some items are out of stock',
                'details': out_of_stock_items
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Cart is valid for checkout'})

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'checkout'

    def post(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        shipping_address = serializer.validated_data['shipping_address_id']
        billing_address = serializer.validated_data['billing_address_id']
        coupon_code = serializer.validated_data.get('coupon_code')
        coupon = None
        discount_applied = 0

        if coupon_code:
            coupon = get_object_or_404(Coupon, code=coupon_code)
            if not coupon.is_valid():
                return Response({'error': 'Invalid or expired coupon'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            total_amount = 0
            order_items = []
            for item in cart.items.select_for_update().all():
                product = item.product
                if product.stock < item.quantity:
                    return Response({'error': f'Insufficient stock for {product.name}'}, status=status.HTTP_400_BAD_REQUEST)
                total_amount += product.price * item.quantity
                order_items.append({
                    'product': product,
                    'quantity': item.quantity,
                    'price': product.price
                })

            if coupon:
                discount_applied = total_amount * (coupon.discount_percentage / 100)
                if coupon.max_discount and discount_applied > coupon.max_discount:
                    discount_applied = coupon.max_discount
                total_amount -= discount_applied
                coupon.used_count = F('used_count') + 1
                coupon.save()

            total_amount += total_amount * 0.1 + 10.00

            # Simulate payment processing (10% chance of failure for demo)
            if random.random() < 0.1:
                return Response({'error': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                shipping_address=str(shipping_address),
                billing_address=str(billing_address),
                payment_reference=serializer.validated_data.get('payment_reference', ''),
                status='pending' if random.random() >= 0.1 else 'failed',
                coupon=coupon,
                discount_applied=discount_applied
            )

            for item_data in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                item_data['product'].stock = F('stock') - item_data['quantity']
                item_data['product'].save()

            cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status not in ['pending', 'processing']:
            return Response({'error': f'Cannot cancel order in {order.status} status'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            order.status = 'cancelled'
            for item in order.items.select_for_update().all():
                item.product.stock = F('stock') + item.quantity
                item.product.save()
            order.save()
        return Response(OrderSerializer(order).data)

class OrderReturnView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status not in ['delivered']:
            return Response({'error': f'Cannot return order in {order.status} status'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            order.status = 'returned'
            for item in order.items.select_for_update().all():
                item.product.stock = F('stock') + item.quantity
                item.product.save()
            order.save()
        return Response(OrderSerializer(order).data)

class OrderRefundView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status not in ['returned']:
            return Response({'error': f'Cannot refund order in {order.status} status'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            order.status = 'refunded'
            order.save()
        return Response(OrderSerializer(order).data)

class OrderItemDetailView(generics.RetrieveAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)
