from schemas import StoreUserSchema, ProductSchema
from core.models import StoreUser
from orders.models import Cart, Order
import httpx

def validate_add_product_inputs(product: ProductSchema, seller: StoreUserSchema):
    if seller.role != "seller":
        raise Exception("Only users with role='seller' can add products")

    required_fields = {
        "email": seller.email,
        "username": seller.username,
        "first_name": seller.first_name,
        "last_name": seller.last_name,
        "password": seller.password,
    }

    missing = [name for name, value in required_fields.items() if not value]
    if missing:
        raise Exception(f"Missing required seller fields: {', '.join(missing)}")
    
    if any([product.quantity < 1, product.price < 1]):
        raise Exception("Product quantity and price must be at least 1")

def user_login_request(seller: StoreUserSchema):
    if seller is None:
        raise Exception("No seller info provided!")

    url = "http://127.0.0.1:8000/users/login/jwt/"
    payload = {
        "email": seller.email,
        "username": seller.username,
        "password": seller.password,
    }
    headers = {"Content-Type": "application/json"}

    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Invalid credentials")
        
def get_user_id(store_user: StoreUserSchema):
    if store_user is None:
        raise Exception("No seller info provided!")
    
    store_user_db = None
    if store_user.email:
        store_user_db = StoreUser.objects.filter(user__email=store_user.email).first()
    else:
        store_user_db = StoreUser.objects.filter(user__username=store_user.username).first()

    return store_user_db.pk

def get_cart_id(store_user_id):
    if store_user_id is None:
        raise Exception("No seller info provided!")
    
    return Cart.objects.filter(store_user_id=store_user_id).first().pk