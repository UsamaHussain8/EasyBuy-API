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
   
    
