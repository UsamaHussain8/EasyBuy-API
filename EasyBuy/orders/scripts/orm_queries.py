from django_extensions import db
from core.models import StoreUser, User
from products.models import Product
from orders.models import Order, OrderItem, Cart, CartItem
from django.db.models import Count, F, Q, Sum
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

def get_electronics_items_or_low_stock_items():
    electronic_low_stock_items = Product.objects.filter(
                                 Q(category__in=['electronics', 'Electronics']) | Q(quantity__lt=5)) \
                                    .values('name', 'category', 'quantity', 'price')
    for product in electronic_low_stock_items:
        print(product)
    pprint(connection.queries)    

def get_customers_with_more_orders():
    customers_with_one_or_more_orders = StoreUser.objects.filter(
                                 Q(contact_number__endswith='7') | Q(num_orders__gt=1)) \
                                 .annotate(username=F('user__username'), 
                                           email=F('user__email')) \
                                 .values('username', 'email', 'contact_number', 'num_orders')
    for user in customers_with_one_or_more_orders:
        print(user)
    pprint(connection.queries)     

def count_number_of_products():
    num_products = Product.objects.count()
    print(num_products)

    pprint(connection.queries)

def revenue_from_completed_orders():
    total_revenue_completed_orders = Order.objects.filter(status="COMPLETED").aggregate(total_revenue=Sum('total_amount'))
    print(total_revenue_completed_orders)

    pprint(connection.queries)

####################################################    
def run(): 
    """
    Get all products with quantity less than 10
    """
    # get_low_quantity_products()

    """
    Get all buyers who have placed at least one order
    """
    # get_buyers_list()

    """
    Find all orders with payment method = EASYPAISA OR NAYAPAY
    """
    # get_easypaisa_nayapay_payment_orders()

    """
    Find products with category = electronics OR with low stock
    """
    # get_electronics_items_or_low_stock_items()

    """
    Find all buyers whose contact_number ends with '7' OR who have more than 1 order
    """
    # get_customers_with_more_orders()

    """
    Find total number of products in the database
    """
    # count_number_of_products()

    """
    Calculate total revenue from all COMPLETED orders
    """
    revenue_from_completed_orders()