from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer
from products.models import Product

class CartDetailView(generics.RetrieveAPIView):
    """
    Retrieve the logged-in user's cart.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(store_user=self.request.user.store_user)
        return cart


class CartItemAddView(generics.CreateAPIView):
    """
    Add an item to the cart (or update if it already exists).
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        store_user = request.user.store_user
        cart, _ = Cart.objects.get_or_create(store_user=store_user)

        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)

        # Check if item already exists
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemDeleteView(generics.DestroyAPIView):
    """
    Remove a specific item from the cart.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cart = get_object_or_404(Cart, store_user=self.request.user.store_user)
        return cart.cartitem_set.all()


class OrderListView(generics.ListAPIView):
    """
    List all orders of the current user.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(store_user=self.request.user.store_user).order_by('-ordered_at')


class OrderDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single order with all details.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(store_user=self.request.user.store_user)


class OrderCreateView(generics.CreateAPIView):
    """
    Create a new order based on the user's cart.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        store_user = request.user.store_user
        cart = get_object_or_404(Cart, store_user=store_user)
        cart_items = cart.cartitem_set.all()

        if not cart_items.exists():
            return Response({"detail": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        # Create order
        order = Order.objects.create(
            store_user=store_user,
            cart=cart,
            total_amount=total_amount,
            shipping_address=request.data.get("shipping_address", ""),
            payment_method=request.data.get("payment_method", "CASH_ON_DELIVERY")
        )

        # Create order items & reduce stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
            item.product.quantity -= item.quantity
            item.product.save()

        # Empty the cart
        cart_items.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
