from django.db import models
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from core.models import StoreUser

class Tag(models.Model):
    caption = models.CharField(max_length=20)
    def __str__(self):
        return self.caption

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('fashion', 'Fashion'),
        ('books', 'Books'),
        ('toys', 'Toys'),
        ('mobiles', 'Mobiles'),
        ('laptops', 'Laptops'),
        ('accessories', 'Accessories'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=50, null=False)
    slug = models.SlugField(null=False, blank=False, unique=True)
    price = models.PositiveIntegerField(null=False, default=1)
    quantity = models.PositiveIntegerField(null=False, default=1)
    category = models.CharField(max_length=50, default='', null=False, choices=CATEGORY_CHOICES)
    description = models.TextField(null=True, default='')
    excerpt = models.CharField(max_length=150, default='', null=False)
    tags = models.ManyToManyField(Tag)
    # Each product can have only one seller and one seller can sell/create many products
    seller = models.ForeignKey(StoreUser, on_delete=models.CASCADE, null=False)

    def __str__(self) -> str:
        return f"{self.name} costs {self.price}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = f"{base_slug}-{self.seller.user.id}"
        return super().save(*args, **kwargs)

class Review(models.Model):
    rating = models.PositiveIntegerField(null=False, validators=[MaxValueValidator(5), MinValueValidator(1)])
    review = models.TextField(null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(StoreUser, on_delete=models.CASCADE, related_name='user_reviews')

    def __str__(self):
        return f"{self.reviewer} - {self.rating}"