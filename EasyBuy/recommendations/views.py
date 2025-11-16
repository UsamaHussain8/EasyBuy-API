from rest_framework.views import APIView
from rest_framework.response import Response
from products.serializers import ProductSerializer
from .services import get_recommendations_for_user
from products.models import Product
from .models import RecommendationModel

class UserRecommendationView(APIView):
    def get(self, request, user_id):
        products = get_recommendations_for_user(user_id)
        serializer = ProductSerializer(products, many=True)
        return Response({"recommended_products": serializer.data})
    
# class RecommendView(APIView):
    # permission_classes = [IsAuthenticated]

    # def get(self, request):
    #     user = request.user

    #     # 1. Ensure StoreUser exists
    #     try:
    #         store_user = user.storeuser
    #     except:
    #         return Response(
    #             {"detail": "Store user profile not found."},
    #             status=400
    #         )

    #     # 2. Load trained model  
    #     try:
    #         model = RecommendationModel.load()
    #     except FileNotFoundError:
    #         return Response(
    #             {"detail": "Recommender model not built yet."},
    #             status=503
    #         )

    #     # 3. Ask model for recommendations 
    #     product_ids = model.recommend_for_user(store_user.id, top_n=10)

    #     # 4. Cold-start fallback (if no recommendations)
    #     if not product_ids:
    #         fallback_products = Product.objects.order_by("-created_at")[:10]
    #         serializer = ProductSerializer(
    #             fallback_products, many=True, context={"request": request}
    #         )
    #         return Response({
    #             "recommendations": serializer.data,
    #             "cold_start": True
    #         })

    #     # 5. Fetch product objects
    #     products = Product.objects.filter(id__in=product_ids)

    #     serializer = ProductSerializer(
    #         products, many=True, context={"request": request}
    #     )

    #     return Response({
    #         "recommendations": serializer.data,
    #         "cold_start": False
    #     })