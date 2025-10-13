from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from .models import StoreUser
from .serializers import UserSerializer, StoreUserSerializer

@login_required(login_url='login_view')
def profile(request, id):
    user = StoreUser.objects.select_related().filter(id=id).first()
    return render(request, "core/profile.html", context={"user": user})

@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def get_users(request):
    all_users = User.objects.select_related('store_user').all()
    serializer = UserSerializer(all_users, many=True)
    return Response(serializer.data)
