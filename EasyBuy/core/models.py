from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

class StoreUser(models.Model):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store_user')
    contact_number = models.CharField(max_length=13, validators=[RegexValidator(r'^\+92[0-9]{10}$')], null=False, blank=False, unique=True)
    num_orders = models.PositiveIntegerField(default=0, null=False)
    address = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=50, default='buyer', null=False, choices=ROLE_CHOICES)

    def __str__(self):
        return f"StoreUser(user={self.user.username}, with contact_number={self.contact_number} and is a: {self.role})"
    
    def __repr__(self):
        return f"StoreUser(user={self.user.username}, with contact_number={self.contact_number} and is a: {self.role})"
