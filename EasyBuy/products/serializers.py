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
    tags = TagSerializer(many=True)
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

    @transaction.atomic()
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        product = Product.objects.create(**validated_data)
        for tag_data in tags:
            tag_obj, _ = Tag.objects.get_or_create(**tag_data)
            product.tags.add(tag_obj)

        return product