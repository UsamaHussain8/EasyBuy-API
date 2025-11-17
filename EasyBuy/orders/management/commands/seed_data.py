import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from django.db import transaction
from decimal import Decimal

from core.models import StoreUser
from products.models import Product, Tag, Review
from orders.models import Cart, CartItem, Order, OrderItem

fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with demo E-commerce data."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # self.stdout.write(self.style.WARNING("Clearing old data..."))
        # self.clear_data()

        self.stdout.write(self.style.WARNING("Seeding new data..."))
        self.create_users(30)
        self.create_tags(10)
        self.create_products(60)
        self.create_reviews()
        self.create_carts()
        self.create_orders()

        self.stdout.write(self.style.SUCCESS("Database seeding completed."))

    # ------------------------------------------------------------------
    def clear_data(self):
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        Review.objects.all().delete()

    # ------------------------------------------------------------------
    def create_users(self, count):
        self.buyers = []
        self.sellers = []

        for _ in range(count):
            username = fake.unique.user_name()
            email = fake.unique.email()

            user = User.objects.create_user(
                username=username,
                email=email,
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )

            role = random.choice(["buyer", "seller"])

            store_user = StoreUser.objects.create(
                user=user,
                role=role,
                contact_number=self.generate_contact(),
                address=fake.address(),
                num_orders=0,
            )

            if role == "buyer":
                self.buyers.append(store_user)
            else:
                self.sellers.append(store_user)

        print(f"Buyers: {len(self.buyers)}, Sellers: {len(self.sellers)}")

    # ------------------------------------------------------------------
    def generate_contact(self):
        return "+92" + "".join([str(random.randint(0, 9)) for _ in range(10)])

    # ------------------------------------------------------------------
    def create_tags(self, count):
        self.tags = []

        for _ in range(count):
            t = Tag.objects.create(caption=fake.word().capitalize())
            self.tags.append(t)

        print(f"Created {len(self.tags)} tags.")

    # ------------------------------------------------------------------
    def create_products(self, count):
        categories = [c[0] for c in Product.CATEGORY_CHOICES]
        self.products = []

        for _ in range(count):
            seller = random.choice(self.sellers)

            p = Product.objects.create(
                name=fake.word().capitalize() + " " + fake.word().capitalize(),
                price=random.randint(300, 50000),
                quantity=random.randint(5, 80),
                category=random.choice(categories),
                description=fake.text(max_nb_chars=200),
                excerpt=fake.text(max_nb_chars=100),
                seller=seller,
            )

            # Add 0–3 tags to each product
            p.tags.add(*random.sample(self.tags, random.randint(0, min(3, len(self.tags)))))

            self.products.append(p)

        print(f"Created {len(self.products)} products.")

    # ------------------------------------------------------------------
    def create_reviews(self):
        self.reviews = []

        for product in self.products:
            # 40% chance to create reviews
            if random.choice([True, False]):
                for _ in range(random.randint(1, 5)):
                    reviewer = random.choice(self.buyers)
                    r = Review.objects.create(
                        product=product,
                        reviewer=reviewer,
                        rating=random.randint(1, 5),
                        review=fake.text(max_nb_chars=120)
                    )
                    self.reviews.append(r)

        print(f"Created {len(self.reviews)} product reviews.")

    # ------------------------------------------------------------------
    def create_carts(self):
        self.carts = []

        for buyer in self.buyers:
            cart = Cart.objects.create(store_user=buyer)
            self.carts.append(cart)

            # Add 1–6 cart items
            for _ in range(random.randint(1, 6)):
                product = random.choice(self.products)
                qty = random.randint(1, min(3, product.quantity))

                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=qty
                )

        print("Carts and items created.")

    # ------------------------------------------------------------------
    def create_orders(self):
        payment_methods = [p[0] for p in Order.PAYMENT_CHOICES]
        statuses = [s[0] for s in Order.STATUS_CHOICES]

        self.orders = []

        for cart in self.carts:

            # 50% chance to convert the cart into an order
            if random.choice([True, False]):
                store_user = cart.store_user

                order = Order.objects.create(
                    store_user=store_user,
                    cart=cart,
                    total_amount=0,  # set later
                    status=random.choice(statuses),
                    shipping_address=store_user.address,
                    payment_method=random.choice(payment_methods)
                )

                total = Decimal("0")

                # Convert cart items → order items
                for ci in cart.cartitem_set.all():
                    item_price = Decimal(ci.product.price)
                    qty = ci.quantity

                    OrderItem.objects.create(
                        order=order,
                        product=ci.product,
                        quantity=qty,
                        price_at_purchase=item_price
                    )

                    total += (item_price * qty)

                order.total_amount = total
                order.save()

                store_user.num_orders += 1
                store_user.save()

                self.orders.append(order)

        print(f"Created {len(self.orders)} orders.")
