from products.models import Product
from core.models import StoreUser
from schemas import ProductSchema, StoreUserSchema
import httpx
from asgiref.sync import sync_to_async
import http

def add_products_to_database(product: ProductSchema, seller: StoreUserSchema, seller_id: int, access_token: str):
    url = "http://127.0.0.1:8000/products/create/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    print("Seller id:", seller_id)

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

