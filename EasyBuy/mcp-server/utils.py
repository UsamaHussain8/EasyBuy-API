from schemas import StoreUserSchema
from core.models import StoreUser
import httpx

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
