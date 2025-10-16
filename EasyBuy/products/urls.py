from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ProductsListApiView.as_view(), name='products_list'),
]
