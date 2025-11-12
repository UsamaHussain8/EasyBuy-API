import os
import pickle
from collections import defaultdict

import pandas as pd
from django.db.models import Prefetch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from products.models import Product, Review
from orders.models import OrderItem, Order
from core.models import StoreUser

MODEL_PATH = os.path.join('models', 'recommender.pkl') 

class Recommender:
    def __init__(self, item_sim=None, product_index=None, products_df=None, config=None):
        """
        item_sim: pandas.DataFrame with item-item similarities (indexed by product.id)
        product_index: map product.id -> integer index used in similarity matrix
        products_df: DataFrame of product info (id, name, category, tags, etc)
        config: dict with hyperparams (weights)
        """
        self.item_sim = item_sim
        self.product_index = product_index or {}
        self.products_df = products_df
        self.config = config or {'content_weight': 0.5, 'collab_weight': 0.5}

    @classmethod
    def build(cls, content_weight=0.5, collab_weight=0.5):
        """
        Build the recommender from DB.
        """
        # 1) Load products and build text features
        qs = Product.objects.prefetch_related('tags', 'reviews', 'seller')
        products = []
        for p in qs:
            tags = " ".join([t.caption for t in p.tags.all()])
            reviews_text = " ".join([r.review or "" for r in p.reviews.all()])
            combined = " ".join([p.name or "", p.description or "", tags, reviews_text, p.category or ""])
            products.append({
                'id': p.id,
                'name': p.name,
                'category': p.category,
                'text': combined,
            })
        products_df = pd.DataFrame(products)
        if products_df.empty:
            raise ValueError("No products found in DB")

        # map product id -> index
        product_index = {pid: idx for idx, pid in enumerate(products_df['id'].tolist())}

        # 2) Content similarity: TF-IDF on combined text
        tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
        X_text = tfidf.fit_transform(products_df['text'].fillna(''))
        content_sim = cosine_similarity(X_text)
        content_sim_df = pd.DataFrame(content_sim, index=products_df['id'], columns=products_df['id'])

        # 3) Collaborative similarity from orders/reviews
        # Build user-item interaction matrix. Use rating if exists, else 1 for purchase.
        # Get OrderItems joined with Orders (only completed orders maybe)
        orderitems = OrderItem.objects.select_related('order', 'product')
        # We'll include only completed orders for stronger signal
        orderitems = orderitems.filter(order__status='COMPLETED')

        rows = []
        for oi in orderitems:
            rows.append({
                'user_id': oi.order.store_user.id,
                'product_id': oi.product.id if oi.product else None,
                'quantity': oi.quantity,
            })
        orders_df = pd.DataFrame(rows)
        if orders_df.empty:
            # fallback to reviews if no completed orders
            reviews = Review.objects.select_related('reviewer', 'product')
            rows = [{'user_id': r.reviewer.id, 'product_id': r.product.id, 'rating': r.rating} for r in reviews]
            orders_df = pd.DataFrame(rows)
        # Combine with reviews (explicit ratings) to enrich the matrix
        reviews = Review.objects.select_related('reviewer', 'product')
        rev_rows = []
        for r in reviews:
            rev_rows.append({'user_id': r.reviewer.id, 'product_id': r.product.id, 'rating': r.rating})
        reviews_df = pd.DataFrame(rev_rows)

        # pivot: user x product
        if not orders_df.empty:
            # convert quantity -> implicit interest score
            orders_df['score'] = orders_df['quantity'].fillna(1).astype(float)
            # keep max if multiple purchases
            purchases = orders_df.groupby(['user_id', 'product_id'])['score'].sum().reset_index()
            pivot = purchases.pivot_table(index='user_id', columns='product_id', values='score', fill_value=0)
        else:
            pivot = pd.DataFrame()

        if not reviews_df.empty:
            if pivot.empty:
                pivot = reviews_df.pivot_table(index='user_id', columns='product_id', values='rating', fill_value=0)
            else:
                # merge reviews into pivot (additive)
                reviews_piv = reviews_df.pivot_table(index='user_id', columns='product_id', values='rating', fill_value=0)
                pivot = pivot.add(reviews_piv, fill_value=0)

        if pivot.empty:
            # no collaborative data; use content-only
            collab_sim_df = pd.DataFrame(0, index=products_df['id'], columns=products_df['id'])
        else:
            # item vectors are columns of pivot; compute item-item cosine similarity
            # ensure columns correspond to product ids in product_index
            pivot = pivot.fillna(0)
            # reorder columns to match products_df ids (if missing, fill zeros)
            cols = products_df['id'].tolist()
            pivot = pivot.reindex(columns=cols, fill_value=0)
            item_matrix = pivot.T.values  # shape (n_items, n_users)
            collab_sim = cosine_similarity(item_matrix)
            collab_sim_df = pd.DataFrame(collab_sim, index=cols, columns=cols)

        # 4) Combine sims
        cw = content_weight
        rw = collab_weight
        combined_sim = cw * content_sim_df + rw * collab_sim_df
        # optionally normalize rows
        # convert to DataFrame indexed by product.id
        combined_sim_df = combined_sim

        model = cls(item_sim=combined_sim_df, product_index=product_index, products_df=products_df,
                    config={'content_weight': cw, 'collab_weight': rw})
        return model

    def save(self, path=MODEL_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'item_sim': self.item_sim,
                'product_index': self.product_index,
                'products_df': self.products_df,
                'config': self.config
            }, f)

    @classmethod
    def load(cls, path=MODEL_PATH):
        with open(path, 'rb') as f:
            data = pickle.load(f)
        return cls(item_sim=data['item_sim'],
                   product_index=data['product_index'],
                   products_df=data['products_df'],
                   config=data.get('config', {}))

    def get_similar_items(self, product_id, top_n=10):
        if product_id not in self.item_sim.index:
            return []
        scores = self.item_sim.loc[product_id].sort_values(ascending=False)
        # drop self
        scores = scores.drop(labels=[product_id], errors='ignore')
        top = scores.head(top_n).index.tolist()
        return top

    def recommend_for_user(self, store_user_id, top_n=10, purchased_penalty=True):
        """
        For a user: take items they purchased/have high rating for, aggregate similarity scores.
        """
        # get user's purchased items and review ratings
        # we prefer DB calls here to stay up-to-date
        try:
            su = StoreUser.objects.get(id=store_user_id)
        except StoreUser.DoesNotExist:
            return []

        # purchases
        orderitems = OrderItem.objects.select_related('order', 'product').filter(order__store_user=su, order__status='COMPLETED')
        purchased_ids = [oi.product.id for oi in orderitems if oi.product]
        # reviews
        reviews = Review.objects.filter(reviewer=su).select_related('product')
        rated_ids = [r.product.id for r in reviews if r.product]

        seed_items = list(set(purchased_ids + rated_ids))
        if not seed_items:
            # cold start: recommend top popular or by category fallback
            return self._cold_start_recommend(top_n)

        # aggregate similarity scores
        scores = defaultdict(float)
        for pid in seed_items:
            if pid not in self.item_sim.index:
                continue
            sim_series = self.item_sim.loc[pid]
            for other_pid, sim_score in sim_series.items():
                scores[other_pid] += sim_score

        # remove already purchased
        for pid in set(seed_items):
            if purchased_penalty:
                scores.pop(pid, None)
            else:
                scores[pid] *= 0.1

        # sort items by score
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        top_ids = [pid for pid, _ in ranked[:top_n]]
        # fetch product instances (preserve order)
        products = list(Product.objects.filter(id__in=top_ids))
        # sort products in same order as top_ids
        prod_map = {p.id: p for p in products}
        return [prod_map[i] for i in top_ids if i in prod_map]

    def _cold_start_recommend(self, top_n=10):
        # simple fallback — recommend most-reviewed or top-priced or same-category popular
        # We'll return the top products by number of reviews
        qs = Product.objects.annotate(num_reviews=pd.NamedAgg(column='reviews', aggfunc='count')).order_by('-num_reviews')[:top_n]
        return list(qs)
