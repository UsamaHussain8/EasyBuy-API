from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from .models import StoreUser

class UserSerializer(serializers.ModelSerializer):
    #store_user = StoreUserSerializer(required=True)

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'password',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

class StoreUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    class Meta:
        model = StoreUser
        fields = (
            'user',
            'contact_number',
            'address',
            'role',
        )
        extra_kwargs = {
            'role': {'write_only': True}
        }

    def create(self, validated_data):
        user = validated_data.pop('user')
        store_user = validated_data
        # only create users when both serializers contain the cleaned data
        with transaction.atomic():
            # Create user first
            user = User.objects.create_user(**user)
            # Create related StoreUser profile
            store_user = StoreUser.objects.create(user=user, **validated_data)
        return store_user

