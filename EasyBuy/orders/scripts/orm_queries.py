from django_extensions import db
from core.models import StoreUser, User
from products.models import Product
from orders.models import Order, OrderItem, Cart, CartItem
from django.db.models import Count, F
from django.db import connection
from pprint import pprint

def get_low_quantity_products():
    low_quantity_products = Product.objects.filter(quantity__lt = 10).values('name', 'price', 'quantity')
    for product in low_quantity_products:
        print(product)
    print(connection.queries)

def get_buyers_list():
    buyers_with_orders = (
    StoreUser.objects
    .filter(num_orders__gte=1)
    .select_related('user')
    .annotate(
        email=F('user__email'),
        username=F('user__username'),
        phone=F('contact_number'),
        orders=F('num_orders')
    )
    .values('email', 'username', 'phone', 'orders')
)
    for buyer in buyers_with_orders:
        print(buyer)
    pprint(connection.queries)

def get_easypaisa_nayapay_payment_orders():
    easypaisa_nayapay_payments = Order.objects.filter(payment_method__in=['EASYPAISA', 'NAYAPAY']) \
                                    .values('total_amount', 'ordered_at', 'payment_method')
    for order in easypaisa_nayapay_payments:
        print(order)
    pprint(connection.queries)

def run(): 
    """
    Get all products with quantity less than 10
    """
    # get_low_quantity_products()

    """
    Get all buyers who have placed at least one order
    """
    get_buyers_list()

    """
    Find all orders with payment method = EASYPAISA OR NAYAPAY
    """
    # get_easypaisa_nayapay_payment_orders()