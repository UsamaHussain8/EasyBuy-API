from rest_framework import permissions, generics, status
from django.shortcuts import get_object_or_404
from .models import Product, Review
from .serializers import ProductSerializer, TagSerializer, ReviewSerializer
from .permissions import IsSellerAndOwner, IsReviewAuthorOrReadOnly

class ProductsListApiView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductsCreateApiView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerAndOwner]

class ProductDetailsUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_slug'
    lookup_field = 'slug'
    
    def get_permissions(self):
        self.permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated, IsSellerAndOwner]
        return super().get_permissions()
    
# class ReviewCreateAPIView(generics.CreateAPIView):
#     serializer_class = ReviewSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Review.objects.all()

class ProductReviewView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Return all reviews for the given product slug."""
        slug = self.kwargs.get('slug')
        product = get_object_or_404(Product, slug=slug)
        return Review.objects.filter(product=product)

    def perform_create(self, serializer):
        """Attach product and reviewer before saving."""
        slug = self.kwargs.get('slug')
        product = get_object_or_404(Product, slug=slug)
        serializer.save(product=product, reviewer=self.request.user)

    def get_serializer_context(self):
        """Add product to serializer context for validate() and create()."""
        context = super().get_serializer_context()
        product_slug = self.kwargs['slug']
        product = get_object_or_404(Product, slug=product_slug)
        context['product'] = product
        return context
    
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewAuthorOrReadOnly]