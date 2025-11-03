import os
import sys
import django
from asgiref.sync import sync_to_async

# --- Django setup ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyBuy.settings')
django.setup()

from mcp.server.fastmcp import FastMCP
from products.models import Product
from core.models import StoreUser
from utils import user_login_request, get_seller_id
from actions import add_products_to_database
from schemas import ProductSchema, StoreUserSchema

mcp = FastMCP("EasyBuyMCPServer", host="127.0.0.1", port=8050)


@mcp.tool()
async def add_product(product: ProductSchema, seller: StoreUserSchema):
    """
    Add a product associated with a seller to the EasyBuy database.
    """
    # --- Basic validation ---
    if seller.role != "seller":
        raise Exception("The user must be a seller to add a product")
    if not seller.email or not seller.username:
        raise Exception("Seller must have a valid email and username")
    if not seller.first_name or not seller.last_name:
        raise Exception("Provide first and last name")
    if not seller.password:
        raise Exception("Provide your password")
    if product.quantity < 1:
        raise Exception("Product quantity must be at least 1")
    if product.price < 1:
        raise Exception("Product price must be positive")

    # --- ORM lookup (must be wrapped) ---
    if seller.email:
        storeUserSellerExists = await sync_to_async(
            lambda: StoreUser.objects.filter(user__email=seller.email).exists()
        )()
    else:
        storeUserSellerExists = await sync_to_async(
            lambda: StoreUser.objects.filter(user__username=seller.username).exists()
        )()

    if not storeUserSellerExists:
        raise Exception("Seller not found in database")

    # --- Token and product addition (wrapped) ---
    user_tokens = await sync_to_async(user_login_request)(seller)
    seller_id: int = await sync_to_async(get_seller_id)(seller)
    result = await sync_to_async(add_products_to_database)(
        product, seller, seller_id, user_tokens["access_token"]
    )

    return {"status": "success", "details": result}


if __name__ == "__main__":
    mcp.run(transport="stdio", host="127.0.0.1", port=8050)
