from django.db import models
from django.template.defaultfilters import slugify

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

    def __str__(self) -> str:
        return f"{self.name} costs {self.price}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)