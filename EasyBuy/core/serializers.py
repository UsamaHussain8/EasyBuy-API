from rest_framework import serializers
from .models import StoreUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreUser
        fields = (
            'id',
            ''
        )