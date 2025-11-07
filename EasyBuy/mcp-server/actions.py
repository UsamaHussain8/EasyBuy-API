from products.models import Product
from core.models import StoreUser
from schemas import ProductSchema, StoreUserSchema
import httpx
from asgiref.sync import sync_to_async
import http

def add_user_to_database(store_user: StoreUserSchema):
    url = "http://127.0.0.1:8000/users/create/"
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "user": {
            "email": store_user.email,
            "username": store_user.username,
            "password": store_user.password,
            "first_name": store_user.first_name,
            "last_name": store_user.last_name,
        },
        "contact_number": store_user.contact_number,
        "address": store_user.address,
        "role": store_user.role,
    }

    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers)
        if response.status_code == http.HTTPStatus.CREATED or response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Store User creation failed: {response.status_code} - {response.text}")


def add_products_to_database(product: ProductSchema, seller: StoreUserSchema, seller_id: int, access_token: str):
    url = "http://127.0.0.1:8000/products/create/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    payload = {
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
        "category": product.category,
        "description": product.description,
        "excerpt": product.excerpt,
        "tags": [{"caption": tag.caption} for tag in getattr(product, "tags", [])],
        "seller_id": seller_id,
    }

    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers)
        if response.status_code == http.HTTPStatus.CREATED or response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Product creation failed: {response.status_code} - {response.text}")


def add_to_cart(product_quantity: int, product_id: int, store_user_id: int, access_token: str):
    """
    Add a product to the user's cart.
    """
    url = "http://127.0.0.1:8000/cart/add/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "product_id": product_id,
        "quantity": product_quantity,
        "store_user_id": store_user_id
    }

    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Add to cart failed: {response.text}")
    
def add_order_to_database(cart_id: int, shipping_address: str, payment_method: str, access_token: str):
    """
    Add a product to the user's cart.
    """
    url = "http://127.0.0.1:8000/orders/create/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "shipping_address": shipping_address,
        "payment_method": payment_method
    }

    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Add to cart failed: {response.text}")