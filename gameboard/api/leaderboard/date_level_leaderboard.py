from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from django.db.models import Sum
from django.utils.dateparse import parse_date
from gameboard.games.models import GameSession

import logging

logger = logging.getLogger(__name__)


class DateLeaderboardPagination(PageNumberPagination):
    """Custom pagination for date-level leaderboard views."""

    page_size = 10  # Default to 10 results per page
    page_size_query_param = "page_size"
    max_page_size = 100


class DateLeaderboardView(APIView):
    """
    View to get leaderboard for a specific date.
    """

    pagination_class = DateLeaderboardPagination

    def get(self, request):
        try:
            date_str = request.query_params.get("date")
            if not date_str:
                return Response(
                    {"error": "Date parameter is required (YYYY-MM-DD)."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            date = parse_date(date_str)
            if not date:
                return Response(
                    {"error": "Invalid date format."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            leaderboard_query = (
                GameSession.objects.filter(start_time__date=date)
                .values("contestant", "contestant__name")
                .annotate(total_score=Sum("score"))
                .order_by("-total_score")
            )

            if not leaderboard_query:
                return Response(
                    {"message": "No leaderboard data found for the specified date."},
                    status=status.HTTP_200_OK,
                )

            paginator = self.pagination_class()
            paginated_leaderboard = paginator.paginate_queryset(
                leaderboard_query, request, view=self
            )

            if paginated_leaderboard is None:
                return Response(
                    {"message": "No leaderboard data found for the specified date."},
                    status=status.HTTP_200_OK,
                )

            # Calculate the starting rank for the current page
            page_number = paginator.page.number
            page_size = paginator.page.paginator.per_page
            start_rank = (page_number - 1) * page_size + 1
            for rank, entry in enumerate(paginated_leaderboard, start=start_rank):
                entry["rank"] = rank

            return paginator.get_paginated_response(paginated_leaderboard)

        except Exception as e:
            logger.error(f"Error fetching date-level leaderboard: {e}")
            return Response(
                {"error": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
