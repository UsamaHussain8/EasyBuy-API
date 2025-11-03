from schemas import StoreUserSchema
from core.models import StoreUser
import httpx

def user_login_request(seller: StoreUserSchema):
    if seller is None:
        raise Exception("Seller is None!")

    url = "http://127.0.0.1:8000/users/login/jwt/"
    payload = {
        "email": seller.email,
        "username": seller.username,
        "password": seller.password,
    }
    headers = {"Content-Type": "application/json"}

    print(seller.email)
    print(seller.username)
    print(seller.password)

    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers)
        print(response.json())
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Invalid credentials")
        
def get_seller_id(seller: StoreUserSchema):
    if seller is None:
        raise Exception("Seller must be a real object")
    
    store_user = None
    if seller.email:
        store_user = StoreUser.objects.filter(user__email=seller.email).first()
    else:
        store_user = StoreUser.objects.filter(user__username=seller.username).first()

    return store_user.pk