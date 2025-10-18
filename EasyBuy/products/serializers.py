from rest_framework import serializers
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Product, Tag
from core.models import StoreUser
from core.serializers import StoreUserSerializer, UserSerializer

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