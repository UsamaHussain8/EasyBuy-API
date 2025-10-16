from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer, TagSerializer

class ProductsListApiView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
