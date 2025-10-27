from django.urls import path
from .views import (
    CartDetailView, CartItemAddView, CartItemDeleteView,
    OrderListView, OrderDetailView, OrderCreateView
)

urlpatterns = [
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/', CartItemAddView.as_view(), name='cart-add'),
    path('cart/items/<int:pk>/delete/', CartItemDeleteView.as_view(), name='cart-item-delete'),

    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
]
