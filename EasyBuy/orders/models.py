from django.db import models
from core.models import StoreUser
from products.models import Product
from django.core.exceptions import ValidationError

class Cart(models.Model):
    store_user = models.OneToOneField(StoreUser, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.store_user.user.username} has a cart worth {self.total_amount}'
    
    def calculate_total_price(self):
        cart_items = self.cartitem_set.all()  # Get all cart items associated with the cart
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        return total_price
    
    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total_price()
        return super().save(*args, **kwargs)
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product} with {self.quantity} number of items'

    def clean(self):
        if self.quantity > self.product.quantity:
            raise ValidationError(f"Only {self.product.quantity} items available in stock.")
        
    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure validation is applied
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('CASH_ON_DELIVERY', 'Cash_On_Deliery'),
        ('EASYPAISA', 'Easypaisa'),
        ('NAYAPAY', 'NayaPay'),
        ('STRIPE', 'Stripe'),
    ]

    store_user = models.ForeignKey(StoreUser, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    ordered_at = models.DateTimeField(auto_now_add=True)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='CASH_ON_DELIVERY')

    def __str__(self):
        return f'Order {self.id} by {self.store_user.user.username}'
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)  # Price of the product at the time of purchase

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in Order {self.order.id}'