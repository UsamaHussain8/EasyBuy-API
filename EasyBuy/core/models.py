from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User, AbstractBaseUser, AbstractUser, BaseUserManager

# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, username, first_name, last_name, contact_number, address, password=None, **extra_fields):
#         if not all([email, username, contact_number, first_name, last_name, address]):
#             raise ValueError("Required field(s) missing")
        
#         email = self.normalize_email(email)
#         user = self.model(
#             email=email,
#             username=username,
#             first_name=first_name,
#             last_name=last_name,
#             contact_number=contact_number,
#             address=address,
#             **extra_fields
#         )
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, username, first_name, last_name, contact_number, address, password=None, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         extra_fields.setdefault("role", "admin")

#         if extra_fields.get("is_staff") is not True:
#             raise ValueError("Superuser must have is_staff set to True.")
#         if extra_fields.get("is_superuser") is not True:
#             raise ValueError("Superuser must have is_superuser to True.")
#         if extra_fields.get("role") != "admin":
#             raise ValueError("Superuser must have role = Admin.")        
#         return self.create_user(email, username, first_name, last_name, contact_number, address, password, **extra_fields)
    
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

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ['username', 'contact_number', 'address']

    def __str__(self):
        return f"StoreUser(user={self.user.username}, with contact_number={self.contact_number} and is a: {self.role})"
    
    def __repr__(self):
        return f"StoreUser(user={self.user.username}, with contact_number={self.contact_number} and is a: {self.role})"