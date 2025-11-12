## EasyBuy-API

EasyBuy API is a RESTful backend built with Django REST Framework (DRF) that powers a basic e-commerce platform.
It supports **user registration, authentication (JWT & standard login), product management, cart handling, and order placement.**

### Features

👤 User Management

Register new users (buyer or seller)
Login with or without JWT authentication
Retrieve user details

🛒 Shopping Cart

Add items to the cart
View all items in the cart with total amount
Remove items from the cart

📦 Orders

Create orders based on items in the cart
View order history
View specific order details

🧑‍💼 Seller Features

Add and manage products (with tags and categories)
Each product is associated with a seller


### 🏗️ Project Setup

1. Clone the Repository
   
   ``` git clone https://github.com/<your-username>/EasyBuy-API.git ```
   
   ``` cd EasyBuy-API ```

2. Create and Activate a Virtual Environment

    ``` python -m venv env-name ```
  
   ##### Activating the environment in Windows   
   
   ``` env-name\Scripts\activate ```

   ##### Activating the environment in macOS/Linux
   
   ``` source env-name/bin/activate ```

    Or if you prefer **uv** (recommended) 
    
      ``` uv venv env-name ```
      

    ##### Activating the environment in Windows:

    ``` env-name\Scripts\activate ```

   ##### Activating the environment in macOS/Linux

   ``` source env-name/bin/activate ```

3. Install Dependencies

   ``` uv pip install -r requirements.txt ```

4. Apply Database Migrations

   ``` python manage.py makemigrations ```
   
   ``` python manage.py migrate ```

5. Set the Environment Variables

   Create a .env file in the same folder that contains ``` manage.py ``` file.

   Add the following variables:

   - Secret Key (provided by Django project in the ``` settings.py ``` file.
   - Debug (True or False, determines whether you want to run the program in Debug mode, TRUE by default.
   - Database Name
   - Database User
   - Database Password
   - Database Host
   - Database Port
  First, create a database (PostgreSQL was used in this project) and then populate the Database variables in the .env file

7. Run the Development Server

   ``` python manage.py runserver ```

   Your API will be available at: (http://127.0.0.1:8000/)
   
    
### 🔑 Authentication

This project supports both session-based login and JWT-based authentication.

   * Non-JWT Login:
   ``` POST /users/login/ ```

   * JWT Login:
   ``` POST /users/login/jwt/ ```

   JWT tokens must be added in the ``` Authorization ``` header:
   ``` Authorization: Bearer <your_access_token> ```

### API Endpoints Overview

##### 👥 User Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/users/create/` | Register a new user |
| `POST` | `/users/login/` | Login without JWT |
| `POST` | `/users/login/jwt/` | Login using JWT |
| `POST` | `/users/<int:id>/` | Retrieve user details |

#####  🛒 Cart Endpoints
| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/cart/` | View current user’s cart |
| `POST` | `/cart/add/` | Add item to cart |
| `DELETE` | `/cart/items/<int:pk>/delete/` | Remove an item from the cart |

#####  📦 Order Endpoints
| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/orders/` | List all user orders |
| `GET` | `/orders/<int:pk>/` | Retrieve a specific order |
| `POST` | `/orders/create/` | Create a new order from cart |

### 💬 Example API Requests
Here are example HTTP requests (for use with Postman or VS Code REST Client):

#### Register a New User

```
POST http://127.0.0.1:8000/users/create/
Content-Type: application/json

{
  "username": "example_user",
  "email": "example_user@example.com",
  "first_name": "Name1",
  "last_name": "Name2",
  "password": "myPassword!",
  "contact_number": "+923xxxxxxxx",
  "address": "Abc, XYZ",
  "role": "seller"
}
```

#### Login (JWT)

```
POST http://127.0.0.1:8000/users/login/jwt/
Content-Type: application/json

{
  "email": "example_user@example.com",
  "password": "myPassword!"
}
```

#### Add a Product (Seller Only)

```
POST http://127.0.0.1:8000/products/create/
Content-Type: application/json
Authorization: Bearer <your_jwt_token>

{
  "name": "Product",
  "price": 100,
  "quantity": 3,
  "category": "xyz",
  "description": "product-qualities",
  "excerpt": "Product xyz with abc features",
  "tags": [
    {"caption": "xyz"}
  ],
  "seller_id": 1
}
```

#### Add Item to Cart
```
POST http://127.0.0.1:8000/cart/add/
Content-Type: application/json
Authorization: Bearer <your_jwt_token>

{
  "product_id": 3,
  "quantity": 2
}
```

#### Place Order
```
POST http://127.0.0.1:8000/orders/create/
Content-Type: application/json
Authorization: Bearer <your_jwt_token>

{
  "shipping_address": "Street 42, XYZ",
  "payment_method": "CASH_ON_DELIVERY"
}
```

### Notes

* The seller must be logged in to create products.

* The buyer must be logged in to add items to the cart or place orders.

* JWT tokens expire after a set duration; regenerate them by logging in again.

### Tech Stack

* Backend Framework: Django, Django REST Framework

* Database: PostgreSQL (for local testing)

* Authentication: JWT (via Djoser)

* Environment: Python 3.11+
