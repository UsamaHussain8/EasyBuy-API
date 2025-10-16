from rest_framework import serializers
from django.db import transaction
from .models import Product, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'caption'
        ]

class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(required=True, many=True)
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
        ]