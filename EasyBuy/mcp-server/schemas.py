from pydantic import BaseModel, Field, constr
from typing import List, Optional, Annotated

class TagSchema(BaseModel):
    """
    Minimal tag representation for Product.tags ManyToMany relation.
    """
    caption: str

class ProductSchema(BaseModel):
    """
    Pydantic equivalent for the Product model.
    Represents data required to create or display a product.
    """
    name: str = Field(..., max_length=50, description="Product name")
    price: int = Field(..., gt=0, description="Positive integer price of the product in Rupees")
    quantity: int = Field(..., gt=0, description="Available quantity of the product")
    category: str = Field(..., description="Product category (must be one of predefined choices)")
    description: Optional[str] = Field("", description="Detailed product description")
    excerpt: Optional[str] = Field("", max_length=150, description="Short product summary")
    tags: Optional[List[TagSchema]] = Field(default_factory=list, description="List of tags associated with the product")

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "name": "Wireless Mouse",
                "price": 1500,
                "quantity": 20,
                "category": "electronics",
                "description": "High precision 2.4GHz wireless mouse with ergonomic design.",
                "excerpt": "Ergonomic wireless mouse",
                "tags": [{"caption": "gadgets"}, {"caption": "wireless"}]
            }
        }


class StoreUserSchema(BaseModel):
    """
    Combined schema for the StoreUser model and its related User model fields.
    This includes user-level info (username, email, first/last name) so
    MCP tools or API clients can supply all seller details in one object.
    """
    username: str = Field(..., description="Username of the Django user account")
    email: str = Field(..., description="Email of the user")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    password: str = Field(..., description="Password for authentication")
    contact_number: Annotated[str, Field(pattern=r'^\+92[0-9]{10}$', description="Pakistani phone number in +92XXXXXXXXXX format")]
    num_orders: int = Field(default=0, description="Number of orders placed or received by the user")
    address: Optional[str] = Field(None, description="User's address")
    role: str = Field(default="buyer", description="Role of the user, either 'buyer' or 'seller'")

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "username": "ali_seller",
                "email": "ali@example.com",
                "first_name": "Ali",
                "last_name": "Raza",
                "password": "SecurePass123",
                "contact_number": "+923001112223",
                "num_orders": 0,
                "address": "Lahore, Pakistan",
                "role": "seller"
            }
        }
