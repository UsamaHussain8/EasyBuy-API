# recommendations/services.py

from products.models import Product
from orders.models import OrderItem
from django.db.models import Count
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import RecommendationModel

def train_recommender():
    """
    Trains collaborative + content-based model and stores results in DB.
    """

    # ----------------------------------------------------
    # STEP 1 — COLLABORATIVE FILTERING (USER → PRODUCTS)
    # ----------------------------------------------------
    order_items = OrderItem.objects.values("order__store_user", "product").annotate(
        num=Count("product")
    )

    if not order_items:
        print("No order data yet—training skipped.")
        return None

    users = sorted({i["order__store_user"] for i in order_items})
    products = sorted({i["product"] for i in order_items})
    user_index = {u:i for i,u in enumerate(users)}
    product_index = {p:i for i,p in enumerate(products)}

    # Build user-item matrix
    matrix = np.zeros((len(users), len(products)))
    for item in order_items:
        u = user_index[item["order__store_user"]]
        p = product_index[item["product"]]
        matrix[u][p] += 1          # implicit feedback: #times purchased

    # User similarity
    user_sim = cosine_similarity(matrix)

    user_recommendations = {}

    for user in users:
        uidx = user_index[user]

        # Get similar users sorted
        similar_users = np.argsort(-user_sim[uidx])[1:6]

        # Products current user already bought
        purchased = set(
            OrderItem.objects.filter(order__store_user=user)
            .values_list("product", flat=True)
        )

        recommended_ids = set()

        for s in similar_users:
            for pid, val in enumerate(matrix[s]):
                if val > 0 and products[pid] not in purchased:
                    recommended_ids.add(products[pid])

        # Add top N
        user_recommendations[user] = list(recommended_ids)[:10]

    # ----------------------------------------------------
    # STEP 2 — CONTENT BASED (TAGS + CATEGORY)
    # ----------------------------------------------------
    all_products = Product.objects.all()
    prod_ids = [p.id for p in all_products]

    # vector: [category, tags...]
    vectors = []
    for p in all_products:
        tag_names = list(p.tags.values_list("caption", flat=True))
        vec = [p.category] + tag_names
        vectors.append(vec)

    # convert to numeric features using one-hot encoding
    all_features = list({f for v in vectors for f in v})
    encoded = []

    for v in vectors:
        encoded.append([1 if f in v else 0 for f in all_features])

    encoded = np.array(encoded)
    sim = cosine_similarity(encoded)

    product_similarity = {}
    for i,pid in enumerate(prod_ids):
        # top 10 similar
        top = np.argsort(-sim[i])[1:11]
        product_similarity[pid] = [prod_ids[j] for j in top]

    # ----------------------------------------------------
    # Step 3 — Save trained model
    # ----------------------------------------------------
    RecommendationModel.objects.all().delete()

    return RecommendationModel.objects.create(
        user_recommendations=user_recommendations,
        product_similarity=product_similarity,
    )

def get_recommendations_for_user(user_id):
    model = RecommendationModel.objects.order_by("-trained_at").first()
    if not model:
        return Product.objects.all()[:10]  # nothing trained yet

    # -------------------------
    # 1. User Cold Start
    # -------------------------
    if str(user_id) not in model.user_recommendations:
        # Recommend trending products
        trending = (
            OrderItem.objects.values("product")
            .annotate(cnt=Count("product"))
            .order_by("-cnt")[:10]
        )
        product_ids = [t["product"] for t in trending]
        return Product.objects.filter(id__in=product_ids)

    # Collaborative output
    cf_products = model.user_recommendations[str(user_id)]

    if not cf_products:
        # fallback: popular items
        return Product.objects.all()[:10]

    return Product.objects.filter(id__in=cf_products)
