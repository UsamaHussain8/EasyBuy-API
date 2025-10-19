from django.urls import path, include
from . import views

urlpatterns = [
    path("users/<int:id>/", views.UserDetailView.as_view(), name='get_user_detail'),
    path("users/create/", views.RegisterUserView.as_view(), name="create_new_user"),
    path("users/login/", views.LoginUserView.as_view(), name='login_without_jwt'),
    path("users/login/jwt/", views.LoginUserWithJwtView.as_view(), name='login_with_jwt'),
]
