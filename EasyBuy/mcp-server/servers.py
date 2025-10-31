import os
import django
from fastmcp import FastMCP
from products.models import Product
from core.models import StoreUser
from utils import user_login_request
from actions import add_products_to_database

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyBuy.settings')
django.setup()

mcp = FastMCP("EasyBuyMCPServer")


@mcp.tool()
def add_product(product: Product, seller: StoreUser):
    """
    Add product associated with the seller to the EasyBuy database

    Args:
        product: Details of the product to be added to the database
        seller: Details of the store user who is adding the product to the database
    """
    if seller.role != "seller":
        raise Exception("The user must be a seller to add a product")
    if seller.user.email == None or seller.user.email == "":
        raise Exception("Provide a valid email")
    if seller.user.username == None or seller.user.username == "":
        raise Exception("Provide a valid username")
    if seller.user.first_name == None or seller.user.first_name == "" or seller.user.last_name == None or seller.user.last_name == "":
        raise Exception("Provide a valid first and last name")
    if seller.user.password == None or seller.user.password == "":
        raise Exception("Provide your password")
    if product.quantity <= 1: 
        raise Exception("Product quantity must be at least 1")
    if product.price <= 1:
        raise Exception("Product can not have a price of less than One Rupees")
    if product.name == None or product.name == "":
        raise Exception("Proper proper product name")

    storeUserSeller = None
    if seller.user.username:
        storeUserSeller = StoreUser.objects.filter(user__username=seller.user.username)
    elif seller.user.email:
        storeUserSeller = StoreUser.objects.filter(user__email=seller.user.email)

    user_tokens = user_login_request(storeUserSeller)
    add_products_to_database(product, seller, user_tokens["access_token"])

if __name__ == '__main__':
    mcp.run()