import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import StoreUser
from products.models import Product

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def buyer_user(db):
    user = User.objects.create_user(username="buyer1", password="pass123")
    StoreUser.objects.create(user=user, contact_number="+921111111111", role="buyer")
    return user

@pytest.fixture
def seller_user(db):
    user = User.objects.create_user(username="seller1", password="pass123")
    store_user = StoreUser.objects.create(user=user, contact_number="+922222222222", role="seller")
    return user

@pytest.fixture
def seller_product(seller_user):
    store_user = seller_user.store_user
    return Product.objects.create(
        name="Laptop",
        slug="laptop",
        price=2000,
        quantity=5,
        category="electronics",
        description="A powerful laptop",
        excerpt="Laptop for sale",
        seller=store_user,
    )

@pytest.mark.django_db
def test_buyer_cannot_create_product(api_client, buyer_user):
    api_client.force_authenticate(user=buyer_user)

    data = {
        "name": "Toy Car",
        "slug": "toy-car",
        "price": 500,
        "quantity": 10,
        "category": "toys",
        "description": "A cool toy car",
        "excerpt": "Fun car",
        "seller": buyer_user.store_user.id,
    }

    response = api_client.post(reverse('products_creation'), data, format="json")
    assert response.status_code == 403  # forbidden


@pytest.mark.django_db
def test_seller_can_create_product(api_client, seller_user):
    api_client.force_authenticate(user=seller_user)

    data = {
        "name": "New Phone",
        "slug": "new-phone",
        "price": 1000,
        "quantity": 3,
        "category": "mobiles",
        "description": "Latest smartphone",
        "excerpt": "Fast and sleek",
        "seller": seller_user.store_user.id,
    }

    response = api_client.post(reverse('products_creation'), data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "New Phone"

@pytest.mark.django_db
def test_seller_cannot_edit_others_product(api_client, seller_user, seller_product):
    # Create another seller
    other_seller = User.objects.create_user(username="seller2", password="pass123")
    StoreUser.objects.create(user=other_seller, contact_number="+923333333333", role="seller")

    api_client.force_authenticate(user=other_seller)

    url = f"/products/{seller_product.id}/"
    response = api_client.put(url, {"price": 3000}, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN  # forbidden


@pytest.mark.django_db
def test_seller_can_edit_own_product(api_client, seller_user, seller_product):
    api_client.force_authenticate(user=seller_user)

    url = f"/api/products/{seller_product.id}/"
    response = api_client.put(url, {"price": 3000}, format="json")

    assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_202_ACCEPTED]
