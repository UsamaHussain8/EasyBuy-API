from products.models import Product
from core.models import StoreUser
import httpx

async def user_login_request(seller: StoreUser):
    if seller is None:
        raise Exception("Seller is none!")
    
    url = "http://127.0.0.1:8000/users/login/jwt/"
    payload = {
        "email": seller.user.email,
        "username": seller.user.username,
        "password": seller.user.password,
    }
    headers = {"Content-Type": "application/json"}

    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception("Invalid credentials")