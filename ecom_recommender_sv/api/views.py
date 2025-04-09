# views.py
import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.utils import timezone

from .models import UserInteraction, ProductFeature
from .serializers import UserInteractionSerializer, ProductFeatureSerializer, RecommendationRequestSerializer
from .recommendation import RecommendationService

logger = logging.getLogger(__name__)


class RecommendationViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create simple repositories using Django ORM
        class DjangoProductFeatureRepo:
            def get_all_features(self):
                return ProductFeature.objects.all()

        class DjangoInteractionRepo:
            def get_user_interactions(self, user_id):
                return UserInteraction.objects.filter(user_id=user_id)

        self.recommendation_service = RecommendationService(
            DjangoProductFeatureRepo(),
            DjangoInteractionRepo()
        )
    @action(detail=False, methods=['get'])
    def for_user(self, request):
        user_id = request.query_params.get('user_id')
        limit = int(request.query_params.get('limit', 5))

        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        try:
            recommendations = self.recommendation_service.get_recommendations(user_id, limit)
            return Response(recommendations)
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return Response({"error": f"Error generating recommendations: {str(e)}"}, status=500)

    @action(detail=False, methods=['get'])
    def similar_items(self, request):
        product_id = request.query_params.get('product_id')
        limit = int(request.query_params.get('limit', 5))

        if not product_id:
            return Response({"error": "product_id is required"}, status=400)

        try:
            similar_products = self.recommendation_service.get_similar_items(product_id, limit)
            return Response(similar_products)
        except Exception as e:
            logger.error(f"Error finding similar items: {str(e)}")
            return Response({"error": f"Error finding similar items: {str(e)}"}, status=500)

    @action(detail=False, methods=['post'])
    def rebuild_model(self, request):
        try:
            result = self.recommendation_service.rebuild_model()
            return Response(result)
        except Exception as e:
            logger.error(f"Error rebuilding model: {str(e)}")
            return Response({"error": f"Error rebuilding model: {str(e)}"}, status=500)


class InteractionViewSet(viewsets.ModelViewSet):
    queryset = UserInteraction.objects.all()
    serializer_class = UserInteractionSerializer

class ProductFeatureViewSet(viewsets.ModelViewSet):
    queryset = ProductFeature.objects.all()
    serializer_class = ProductFeatureSerializer

@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({"status": "healthy"})