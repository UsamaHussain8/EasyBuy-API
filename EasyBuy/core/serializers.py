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

    def create(self, validated_data):
        store_user_data = validated_data.pop('store_user')

        # only create users when both serializers contain the cleaned data
        with transaction.atomic():
            # Create user first
            user = User.objects.create_user(**validated_data)
            # Create related StoreUser profile
            StoreUser.objects.create(user=user, **store_user_data)
        return user

    # def to_representation(self, instance):
    #     """Ensure nested StoreUser appears when serializing."""
    #     rep = super().to_representation(instance)
    #     if(instance is not None and instance.store_user):
    #         rep['store_user'] = StoreUserSerializer(instance.store_user).data
    #     return rep

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

