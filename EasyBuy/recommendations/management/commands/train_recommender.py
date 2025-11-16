from django.core.management.base import BaseCommand
from recommendations.services import train_recommender

class Command(BaseCommand):
    help = "Train the recommendation model"

    def handle(self, *args, **kwargs):
        model = train_recommender()
        if model:
            self.stdout.write(self.style.SUCCESS("Recommender trained successfully"))
        else:
            self.stdout.write(self.style.WARNING("No training data yet"))
