from products.models import Product
from core.models import StoreUser
import httpx
from asgiref.sync import sync_to_async

async def add_products_to_database(product: Product, seller: StoreUser, access_token):
    """
    Builds a JSON payload dictionary for product creation.
    store_user: StoreUser instance (has .user)
    product: Product instance or object with attributes
    """
    url = "http://127.0.0.1:8000/products/create/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    store_user_id = await sync_to_async(StoreUser.objects.get(user__email=seller.user.email).user.pk)
    payload = {
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
        "category": product.category,
        "description": product.description,
        "excerpt": product.excerpt,
        "tags": [
            {"caption": tag.caption} for tag in product.tags.all()
        ],
        "seller_id": seller.id
    }

    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception("Invalid credentials")