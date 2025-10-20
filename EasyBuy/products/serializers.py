from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Product, Tag, Review
from core.models import StoreUser
from core.serializers import StoreUserSerializer
from orders.models import OrderItem

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'caption'
        ]

class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    seller = StoreUserSerializer(read_only=True)
    seller_id = serializers.PrimaryKeyRelatedField(
        queryset = StoreUser.objects.all(),
        source='seller',
        write_only=True
    )
    class Meta:
        model = Product
        fields = [
            'name',
            'price',
            'quantity',
            'category',
            'description',
            'excerpt',
            'tags',
            'seller',
            'seller_id',
            'reviews',
        ]

    @transaction.atomic()
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        seller = validated_data.pop('seller', None)
        #seller, _ = get_object_or_404(StoreUser, pk=seller_id)
        if not seller:
            raise serializers.ValidationError(
                {"seller_id": "Seller not registered or invalid ID."}
            )
        product = Product.objects.create(**validated_data, seller=seller)
        for tag_data in tags:
            tag_obj, _ = Tag.objects.get_or_create(**tag_data)
            product.tags.add(tag_obj)

        #product.save()
        return product
    
class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.StringRelatedField(read_only=True)
    product = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Review
        fields = ['rating', 'review', 'product', 'reviewer']
        read_only_fields = ['reviewer']

    def validate(self, attrs):
        request = self.context['request']
        reviewer = request.user.store_user
        product = self.context.get('product')

         # Ensure product context is available
        if not product:
            raise serializers.ValidationError("Product not found in context.")
        
        # Check if user purchased this product
        has_purchased = OrderItem.objects.filter(
            order__buyer=reviewer, product=product
        ).exists()

        if not has_purchased:
            raise serializers.ValidationError(
                "You can only review products you've purchased."
            )

        already_reviewed = Review.objects.filter(
            reviewer=reviewer, product=product
        ).exists()

        if already_reviewed:
            raise serializers.ValidationError(
                "You have already reviewed this product."
            )
        
        return attrs

    def create(self, validated_data):
        product = self.context['product']
        reviewer = self.context['request'].user.store_user
        return Review.objects.create(product=product, reviewer=reviewer, **validated_data)