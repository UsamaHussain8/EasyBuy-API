from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from .models import StoreUser
from django.contrib.auth.models import User

@login_required(login_url='login_view')
def profile(request, id):
    user = StoreUser.objects.select_related().filter(id=id).first()
    return render(request, "core/profile.html", context={"user": user})