from django.contrib import admin
from .models import Tag, Product

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',), }

admin.site.register(Tag)
admin.site.register(Product, ProductAdmin)
