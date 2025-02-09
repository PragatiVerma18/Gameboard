import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from django.db.models import Sum
from gameboard.games.models import GameSession, Game

logger = logging.getLogger(__name__)


class GameLeaderboardPagination(PageNumberPagination):
    """Custom pagination for game-wise leaderboard views."""

    page_size = 10  # Default to 10 results per page
    page_size_query_param = "page_size"
    max_page_size = 100


class GameLeaderboardView(APIView):
    """
    View to get the game-wise leaderboard with pagination.
    """

    pagination_class = GameLeaderboardPagination

    def get(self, request, game_id):
        try:
            game = Game.objects.get(id=game_id)

            leaderboard_query = (
                GameSession.objects.filter(game=game)
                .values("contestant", "contestant__name")
                .annotate(total_score=Sum("score"))
                .order_by("-total_score")
            )

            if not leaderboard_query:
                return Response(
                    {"message": "No leaderboard data found for the specified game."},
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

            # Add ranks to the paginated leaderboard
            for rank, entry in enumerate(paginated_leaderboard, start=start_rank):
                entry["rank"] = rank

            return paginator.get_paginated_response(
                {"leaderboard": paginated_leaderboard}
            )

        except Game.DoesNotExist:
            return Response(
                {"error": "Game not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error fetching game leaderboard: {e}")
            return Response(
                {"error": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
