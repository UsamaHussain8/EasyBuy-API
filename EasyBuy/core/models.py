from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

class StoreUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=13, validators=[RegexValidator(r'^\+92[0-9]{10}$')], null=False, blank=False, unique=True)
    num_orders = models.PositiveIntegerField(default=0, null=False)
    address = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.user.username
    
    def __repr__(self):
        return f"StoreUser(user={self.user.username}, contact_number={self.contact_number})"
