# recommendation_service.py

import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd
from collections import defaultdict

class RecommendationService:
    def __init__(self, product_feature_repo, interaction_repo):
        self.product_feature_repo = product_feature_repo
        self.interaction_repo = interaction_repo
        self.model = None
        self.product_mapping = {}
        self.reverse_mapping = {}
        self.feature_pipeline = None
        self.features_array = None

    def rebuild_model(self):
        """Rebuild the recommendation model with consistent feature dimensions"""
        # Get all product features
        product_features = self.product_feature_repo.get_all_features()
        if not product_features:
            return {"status": "error", "message": "No product features available"}

        # Create a mapping of product IDs to indices
        self.product_mapping = {pf.product_id: i for i, pf in enumerate(product_features)}
        self.reverse_mapping = {i: pf.product_id for i, pf in enumerate(product_features)}

        # Extract all features into a DataFrame
        features_data = []
        for pf in product_features:
            feature_dict = pf.features.copy()
            # Add product_id to identify the row
            feature_dict['product_id'] = pf.product_id
            features_data.append(feature_dict)

        df = pd.DataFrame(features_data)

        # Fill missing values
        # For categorical columns (all except 'ram' and 'price_range')
        for col in df.columns:
            if col not in ['ram', 'product_id']:
                df[col] = df[col].fillna('unknown')

        # For numeric columns
        if 'ram' in df.columns:
            df['ram'] = pd.to_numeric(df['ram'], errors='coerce')
            df['ram'] = df['ram'].fillna(df['ram'].median())

        # Ensure all products have the same feature dimensions
        all_keys = set()
        for feature in features_data:
            all_keys.update(feature.keys())

        for feature in features_data:
            for key in all_keys:
                if key not in feature:
                    feature[key] = 'unknown' if key not in ['ram', 'price_range'] else 0

        # Set up feature preprocessing
        categorical_cols = [col for col in df.columns if col not in ['ram', 'product_id', 'price_range']]
        categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)

        numeric_cols = [col for col in ['ram'] if col in df.columns]
        numeric_transformer = StandardScaler()

        # Add price_range as a categorical feature if it exists
        if 'price_range' in df.columns:
            categorical_cols.append('price_range')

        # Create column transformer
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', categorical_transformer, categorical_cols),
                ('num', numeric_transformer, numeric_cols)
            ],
            remainder='drop'
        )

        # Create and fit the pipeline
        self.feature_pipeline = Pipeline([
            ('preprocessor', preprocessor)
        ])

        # Extract product_ids before fitting
        product_ids = df['product_id'].tolist()

        # Fit transform the features
        self.features_array = self.feature_pipeline.fit_transform(df)

        # Create nearest neighbors model
        self.model = NearestNeighbors(n_neighbors=min(10, len(product_ids)), metric='cosine')
        self.model.fit(self.features_array)

        return {"status": "success", "message": "Model rebuilt successfully"}

    def get_recommendations(self, user_id, limit=5):
        # """Get personalized recommendations for a user"""
        # if not self.model or not self.features_array.any():
        #     return []

        # Get user interactions
        interactions = self.interaction_repo.get_user_interactions(user_id)
        if not interactions:
            return []

        # Create user profile based on interactions
        user_profile = defaultdict(int)
        for interaction in interactions:
            product_id = interaction.product_id
            if product_id in self.product_mapping:
                idx = self.product_mapping[product_id]
                # Weight different interaction types
                if interaction.interaction_type == 'view':
                    user_profile[idx] += 1
                elif interaction.interaction_type == 'cart':
                    user_profile[idx] += 3
                elif interaction.interaction_type == 'purchase':
                    user_profile[idx] += 5

        if not user_profile:
            return []

        # Calculate user vector
        user_vector = np.zeros(self.features_array.shape[0])
        for idx, weight in user_profile.items():
            user_vector[idx] = weight

        # Calculate weighted average
        user_profile_vector = np.zeros(self.features_array.shape[1])
        total_weight = sum(user_profile.values())

        for idx, weight in user_profile.items():
            user_profile_vector += (weight / total_weight) * self.features_array[idx]

        # Find nearest neighbors to user profile
        _, indices = self.model.kneighbors([user_profile_vector], n_neighbors=limit+10)

        # Filter out already interacted products
        recommendations = []
        for idx in indices[0]:
            product_id = self.reverse_mapping[idx]
            if product_id not in [interaction.product_id for interaction in interactions]:
                recommendations.append(product_id)
                if len(recommendations) >= limit:
                    break

        return recommendations

    def get_similar_items(self, product_id, limit=5):
        """Get similar items to a given product"""
        if not self.model or product_id not in self.product_mapping:
            return []

        idx = self.product_mapping[product_id]

        # Get nearest neighbors
        distances, indices = self.model.kneighbors([self.features_array[idx]], n_neighbors=limit+1)

        # Skip the first result (which is the product itself)
        similar_products = []
        for i in range(1, min(limit+1, len(indices[0]))):
            similar_products.append({
                "product_id": self.reverse_mapping[indices[0][i]],
                "similarity_score": 1 - distances[0][i]  # Convert distance to similarity
            })

        return similar_products