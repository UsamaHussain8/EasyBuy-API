from django_extensions import db
from core.models import StoreUser, User
from products.models import Product, Review
from orders.models import Order, OrderItem, Cart, CartItem
from django.db.models import Count, F, Q, Sum, Count, Avg
from django.contrib.postgres.aggregates import ArrayAgg
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

def orders_placed_by_customer():
    orders_placed_each_customer = \
        StoreUser.objects.annotate(num_orders_by_customer=Count('num_orders')). \
        annotate(username=F('user__username'), email=F('user__email')). \
        values('id', 'num_orders')
        #filter(num_orders__gt=0)
    print(orders_placed_each_customer)

    pprint(connection.queries)

def avg_rating_per_product():
    rating_per_product = Product.objects.annotate(avg_rating=Avg('reviews__rating')).values('id', 'name', 'avg_rating')
    print(rating_per_product)

    pprint(connection.queries)

def num_reviews_per_product():
    num_reviews_per_product = Product.objects.annotate(review_count=Count('reviews')).values('id', 'name', 'review_count')
    print(num_reviews_per_product)

    pprint(connection.queries)

def total_spent_each_buyer():
    total_spendings_by_buyer = StoreUser.objects.annotate(total_spent=Sum('order__total_amount')).\
                                annotate(username=F('user__username')).values('username', 'total_spent').\
                                order_by('-id')
    print(total_spendings_by_buyer)

    pprint(connection.queries)

def num_products_each_seller():
    num_products_by_seller = \
        StoreUser.objects.filter(role__in=['seller', 'Seller']).\
        annotate(product_count=Sum('product__quantity')).\
        annotate(username=F('user__username')).\
        values('username', 'product_count')
    print(num_products_by_seller)

    pprint(connection.queries)

def num_items_for_each_order():
    num_orderitems_in_order = Order.objects.annotate(item_count=Count('orderitem__quantity')).values('id', 'item_count')
    print(num_orderitems_in_order)

    pprint(connection.queries)

def increase_product_quantities(quantity: int):
    Product.objects.update(quantity=F('quantity') + quantity)
    # Product.save()
    print(Product.refresh_from_db('quantity'))

def fetch_buyer_and_cart():
    buyer_with_cart = Order.objects.select_related('store_user', 'store_user__user', 'cart')
    for buyer in buyer_with_cart:
        print(buyer.store_user.user.username)
        print(buyer.cart.id)

    pprint(connection.queries)

def fetch_product_tags():
    products_with_tags = Product.objects.prefetch_related('tags')
    
    # result = []

    # for p in products_with_tags:
    #     result.append({
    #         'name': p.name,
    #         'tags': [t.caption for t in p.tags.all()]
    #     })
    # pprint(result)
    products_with_tags = (
        Product.objects
        .annotate(
            product_tags=ArrayAgg('tags__caption', distinct=True)
        )
        .values('name', 'product_tags')
    )
    pprint(products_with_tags)

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
    # revenue_from_completed_orders()

    """
    Count how many orders each buyer has placed
    """
    # orders_placed_by_customer()

    """
    Calculate average rating per product
    """
    # avg_rating_per_product()

    """
    Find number of reviews per product
    """
    # num_reviews_per_product()

    """
    Calculate total spendings by each buyer
    """
    # total_spent_each_buyer()

    """
    Calculate number of products each seller sells
    """
    # num_products_each_seller()

    """
    Count number of items in each order
    """
    # num_items_for_each_order()

    """
    Increase product quantity by a passed-in quantity/value
    """
    # increase_product_quantities(1)

    """
    Fetch all orders with store user and cart with single DB query
    """
    fetch_buyer_and_cart()

    """
    Fetch all Products with their Tags
    """
    # fetch_product_tags()