from django.db import models
from django.contrib.postgres.fields import JSONField  

class RecommendationModel(models.Model):
    trained_at = models.DateTimeField(auto_now_add=True)

    # Maps user_id → list of recommended product IDs
    user_recommendations = JSONField(default=dict)

    # For fallback CB recommendations
    product_similarity = JSONField(default=dict)

    def __str__(self):
        return f"Recommender trained on {self.trained_at}"
