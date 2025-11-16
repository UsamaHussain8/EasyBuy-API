from django.urls import path
from .views import UserRecommendationView

urlpatterns = [
    path("user/<int:user_id>/", UserRecommendationView.as_view()),
]