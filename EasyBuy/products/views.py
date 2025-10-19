from rest_framework import permissions, generics, status
from .models import Product
from .serializers import ProductSerializer, TagSerializer
from .permissions import IsSellerAndOwner

class ProductsListApiView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductsCreateApiView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerAndOwner]

class ProductDetailsApiView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_slug'
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]