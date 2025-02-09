from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Count, Sum, Q

from gameboard.games.models import Game, GameSession


class GameDetailsView(APIView):
    """
    API to retrieve details of a game with optimized queries.
    """

    def get(self, request, game_id):
        try:
            game = Game.objects.filter(id=game_id).first()
            if not game:
                return Response(
                    {"error": "Game not found."}, status=status.HTTP_404_NOT_FOUND
                )

            session_data = GameSession.objects.filter(game=game).aggregate(
                active_sessions=Count("id", filter=Q(end_time__isnull=True)),
                total_contestants=Count("contestant", distinct=True),
                total_score=Sum("score"),
            )

            game_data = {
                "id": str(game.id),
                "name": game.name,
                "is_active": game.is_active,
                "upvotes": game.upvotes,
                "active_sessions": session_data["active_sessions"],
                "total_contestants": session_data["total_contestants"],
                "total_score": session_data["total_score"] or 0,
            }

            return Response(game_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
