from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ProductsListApiView.as_view(), name='products_list'),
    path('create/', views.ProductsCreateApiView.as_view(), name='products_creation'),
    path('details/<slug:product_slug>/', views.ProductDetailsUpdateDestroyApiView.as_view(), name='products_detail_update_destroy'),
]
