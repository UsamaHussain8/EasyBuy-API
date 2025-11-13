from django.core.management.base import BaseCommand
from recommender import Recommender, MODEL_PATH
import os

class Command(BaseCommand):
    help = "Build or rebuild the product recommender model"

    def add_arguments(self, parser):
        parser.add_argument('--content-weight', type=float, default=0.5)
        parser.add_argument('--collab-weight', type=float, default=0.5)
        parser.add_argument('--path', type=str, default=MODEL_PATH)

    def handle(self, *args, **options):
        content_w = options['content_weight']
        collab_w = options['collab_weight']
        print("Building recommender (content_w=%s collab_w=%s)..." % (content_w, collab_w))
        model = Recommender.build(content_weight=content_w, collab_weight=collab_w)
        model.save(path=options['path'])
        print("Saved recommender to", options['path'])