import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from django.core.cache import cache
from django.utils.timezone import now

from gameboard.games.models import GamePopularity

logger = logging.getLogger(__name__)


class GamePopularityPagination(PageNumberPagination):
    """Custom pagination for game popularity rankings."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class GamePopularityView(APIView):
    """
    API to fetch the cached popularity index of all games.
    Supports filtering by date, pagination, and continuous ranking.
    """

    pagination_class = GamePopularityPagination

    def get(self, request):
        try:
            date_str = request.query_params.get("date", now().date().isoformat())

            popularity_query = (
                GamePopularity.objects.select_related("game")
                .filter(date=date_str)
                .order_by("-popularity_score")
                .values("game_id", "game__name", "popularity_score")
            )

            if not popularity_query:
                return Response(
                    {"message": "No popularity data found for this date."},
                    status=status.HTTP_200_OK,
                )

            for entry in popularity_query:
                cache_key = f"game_{entry['game_id']}_score"
                entry["popularity_score"] = cache.get(
                    cache_key, entry["popularity_score"]
                )

            paginator = self.pagination_class()
            paginated_results = paginator.paginate_queryset(popularity_query, request)

            page_number = paginator.page.number
            page_size = paginator.page.paginator.per_page
            start_rank = (page_number - 1) * page_size + 1

            for rank, entry in enumerate(paginated_results, start=start_rank):
                entry["rank"] = rank

            return paginator.get_paginated_response({"games": paginated_results})

        except Exception as e:
            logger.error(f"Error fetching game popularity data: {e}")
            return Response(
                {"error": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
