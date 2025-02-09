import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from django.db.models import Sum
from gameboard.games.models import GameSession

logger = logging.getLogger(__name__)


class GlobalLeaderboardPagination(PageNumberPagination):
    """Custom pagination for leaderboard views."""

    page_size = 10  # Default to 10 results per page
    page_size_query_param = "page_size"
    max_page_size = 100


class GlobalLeaderboardView(APIView):
    """
    View to get the global leaderboard with pagination.
    """

    pagination_class = GlobalLeaderboardPagination

    def get(self, request):
        try:
            leaderboard_query = (
                GameSession.objects.values("contestant_id", "contestant__name")
                .annotate(total_score=Sum("score"))
                .order_by("-total_score")
            )

            if not leaderboard_query:
                return Response(
                    {"message": "No leaderboard data found."},
                    status=status.HTTP_200_OK,
                )

            paginator = self.pagination_class()
            paginated_leaderboard = paginator.paginate_queryset(
                leaderboard_query, request
            )

            # Calculate the starting rank for the current page
            page_number = paginator.page.number
            page_size = paginator.page.paginator.per_page
            start_rank = (page_number - 1) * page_size + 1

            for rank, entry in enumerate(paginated_leaderboard, start=start_rank):
                entry["rank"] = rank

            return paginator.get_paginated_response(
                {"leaderboard": paginated_leaderboard}
            )

        except Exception as e:
            logger.error(f"Error fetching global leaderboard: {e}")
            return Response(
                {"error": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
