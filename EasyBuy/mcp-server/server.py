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
from utils import user_login_request, get_user_id, get_cart_id, validate_add_product_inputs
from actions import add_products_to_database, add_user_to_database, add_to_cart, add_order_to_database
from schemas import ProductSchema, StoreUserSchema

mcp = FastMCP("EasyBuyMCPServer", host="127.0.0.1", port=8050)


@mcp.tool()
async def add_user(store_user: StoreUserSchema):
    "Register a new user to the EasyBuy Store"
    if not any([
        store_user.email, store_user.username, store_user.first_name, store_user.last_name, store_user.contact_number, store_user.password
        ]):
        raise Exception("Email, username, first name, last name, contact number and address are required fields")
    
    add_user_to_database(store_user)

@mcp.tool()
async def add_product(product: ProductSchema, seller: StoreUserSchema):
    """
    Add a product associated with a seller to the EasyBuy database.

    Args:
        product (ProductSchema):
            A Pydantic schema instance containing the product details, such as name, price,
            quantity, category, description, excerpt, and optional tags.
        seller (StoreUserSchema):
            A Pydantic schema instance containing the seller’s information and credentials.
            These credentials are used to authenticate the API request and associate the
            newly added product with this seller.

    Returns:
        dict:
            A JSON-decoded dictionary representing the response from the EasyBuy API.
            Typically includes the created product’s details (name, slug, seller, etc.).

    Raises:
        Exception:
            If authentication fails, the API call returns a non-200 response, or any other
            error occurs during the request or database operation.
    """
    validate_add_product_inputs(product, seller)

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

    user_tokens = await sync_to_async(user_login_request)(seller)
    seller_id: int = await sync_to_async(get_user_id)(seller)
    result = await sync_to_async(add_products_to_database)(
        product, seller, seller_id, user_tokens["access_token"]
    )

    return {"status": "success", "details": result}
    
@mcp.tool()
async def add_item_to_cart(product_quantity: int, product_id: int, store_user: StoreUserSchema):
    """
    Adds a specified product to the authenticated store user's cart in the EasyBuy database.

    This function authenticates the provided store user, builds the appropriate JSON payload,
    and sends a POST request to the `/cart/add/` API endpoint to either create a new cart item
    or update the quantity of an existing one.

    Args:
        product_quantity (int):
            The number of units of the specified product to add to the user's cart.
        product_id (int):
            The unique identifier of the product to be added.
        store_user (StoreUserSchema):
            A Pydantic schema instance containing the store user's credentials. These credentials
            are used to authenticate the API request on behalf of the user.

    Returns:
        dict:
            A JSON-decoded dictionary representing the response from the EasyBuy API,
            typically including the updated or newly created cart item details.

    Raises:
        Exception:
            If authentication fails, the product is invalid or out of stock, or the API request
            returns a non-201 (Created) response.
    """
    if not any([store_user, product_quantity, product_id, store_user.username, store_user.email, store_user.password]):
        raise Exception("Please provide essential product and store user data")
    
    if store_user.email:
        storeUserExists = await sync_to_async(
            lambda: StoreUser.objects.filter(user__email=store_user.email).exists()
        )()
    else:
        storeUserExists = await sync_to_async(
            lambda: StoreUser.objects.filter(user__username=store_user.username).exists()
        )()

    if not storeUserExists:
        raise Exception("Please first register to the platform!")

    user_tokens = await sync_to_async(user_login_request)(store_user)
    store_user_id: int = await sync_to_async(get_user_id)(store_user)

    result = await sync_to_async(add_to_cart)(
        product_quantity, product_id, store_user_id, user_tokens["access_token"]
    )

    return {"status": "success", "details": result}

@mcp.tool()
async def place_order(shipping_address: str, payment_method: str, store_user: StoreUserSchema):
    """
    Places a new order for the authenticated store user using the items currently in their cart.

    This function authenticates the store user, calculates the order details based on the user's
    cart, and sends a POST request to the `/orders/create/` endpoint of the EasyBuy API.
    Upon successful execution, the user's cart is cleared and a new order record is created.

    Args:
        shipping_address (str):
            The destination address where the order should be delivered.
        payment_method (str):
            The payment option chosen by the user (e.g., "CASH_ON_DELIVERY", "EASYPAISA",
            "NAYAPAY", or "STRIPE").
        store_user (StoreUserSchema):
            A Pydantic schema instance containing the user's authentication credentials
            and profile information. Used to obtain an access token for API authorization.

    Returns:
        dict:
            A JSON-decoded dictionary containing the created order's details, including
            total amount, ordered items, and order status.

    Raises:
        Exception:
            If authentication fails, the user's cart is empty, or the API request returns
            an error response.
    """
    user_tokens = await sync_to_async(user_login_request)(store_user)
    store_user_id: int = await sync_to_async(get_user_id)(store_user)
    cart_id: int = await sync_to_async(get_cart_id)(store_user_id)
    result = await sync_to_async(add_order_to_database)(cart_id, shipping_address, payment_method, user_tokens["access_token"])

    return {"status": "success", "details": result}


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8050)
