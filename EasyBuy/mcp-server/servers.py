import os
import sys
import django

# --- Add project root to Python path dynamically ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)  # one level up from mcp-server/
sys.path.append(PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyBuy.settings')
django.setup()

from mcp.server.fastmcp import FastMCP
from products.models import Product
from core.models import StoreUser
from utils import user_login_request
from actions import add_products_to_database
from schemas import ProductSchema, StoreUserSchema

mcp = FastMCP("EasyBuyMCPServer", host="127.0.0.1", port=8050)


@mcp.tool()
def add_product(product: ProductSchema, seller: StoreUserSchema):
    """
    Add product associated with the seller to the EasyBuy database

    Args:
        product: Details of the product to be added to the database
        seller: Details of the store user who is adding the product to the database
    """
    if seller.role != "seller":
        raise Exception("The user must be a seller to add a product")
    if seller.email == None or seller.email == "":
        raise Exception("Provide a valid email")
    if seller.username == None or seller.username == "":
        raise Exception("Provide a valid username")
    if seller.first_name == None or seller.first_name == "" or seller.last_name == None or seller.last_name == "":
        raise Exception("Provide a valid first and last name")
    if seller.password == None or seller.password == "":
        raise Exception("Provide your password")
    if product.quantity <= 1: 
        raise Exception("Product quantity must be at least 1")
    if product.price <= 1:
        raise Exception("Product can not have a price of less than One Rupees")
    if product.name == None or product.name == "":
        raise Exception("Proper proper product name")

    storeUserSeller = None
    if seller.username:
        storeUserSeller = StoreUser.objects.filter(user__username=seller.username).first()
    elif seller.email:
        storeUserSeller = StoreUser.objects.filter(user__email=seller.email).first()

    user_tokens = user_login_request(storeUserSeller)
    add_products_to_database(product, seller, user_tokens["access_token"])

if __name__ == '__main__':
    mcp.run(transport="stdio")