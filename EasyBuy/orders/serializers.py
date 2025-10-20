from rest_framework import serializers
from django.db import transaction
from .models import Cart, CartItem, Order, OrderItem
from core.serializers import StoreUserSerializer
from products.serializers import ProductSerializer
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['product', 'product_id', 'quantity']

    def validate(self, attrs):
        """Ensure user cannot add more quantity than available in stock."""
        product = attrs.get('product')
        quantity = attrs.get('quantity', 1)
        if product and quantity > product.quantity:
            raise serializers.ValidationError(
                f"Only {product.quantity} items available in stock."
            )
        return attrs
    
class CartSerializer(serializers.ModelSerializer):
    store_user = StoreUserSerializer(read_only=True)
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['store_user', 'items', 'total_amount']

    def to_representation(self, instance):
        """Recalculate total dynamically."""
        rep = super().to_representation(instance)
        rep['total_amount'] = instance.calculate_total_price()
        return rep
    
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['product', 'product_id', 'quantity', 'price_at_purchase']

class OrderSerializer(serializers.ModelSerializer):
    store_user = StoreUserSerializer(read_only=True)
    items = OrderItemSerializer(source='orderitem_set', many=True)
    cart = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'store_user',
            'cart',
            'total_amount',
            'status',
            'ordered_at',
            'shipping_address',
            'payment_method',
            'items'
        ]
        read_only_fields = ['status', 'ordered_at']

    @transaction.atomic
    def create(self, validated_data):
        """Create order and related order items atomically."""
        items_data = validated_data.pop('orderitem_set', [])
        store_user = self.context['request'].user.store_user

        order = Order.objects.create(store_user=store_user, **validated_data)
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            # Save price at purchase time
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=product.price
            )
            # Deduct stock
            product.quantity -= quantity
            product.save()

        return order