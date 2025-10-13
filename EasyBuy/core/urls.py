from django.urls import path, include
from . import views

urlpatterns = [
    path("profile/<int:id>", views.profile, name="profile"),
    path("users/", views.get_users, name='get_all_users')
]
