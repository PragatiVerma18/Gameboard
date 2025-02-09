from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import F
from gameboard.games.models import Game, GameSession


class ListGameSessionsPagination(PageNumberPagination):
    """
    Custom pagination for game sessions.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class ListGameSessionsView(APIView, ListGameSessionsPagination):
    """
    API to list all sessions of a specific game.
    """

    def get(self, request, game_id):
        try:
            game_exists = Game.objects.filter(id=game_id).exists()
            if not game_exists:
                return Response(
                    {"error": "Game not found."}, status=status.HTTP_404_NOT_FOUND
                )

            sessions = (
                GameSession.objects.filter(game_id=game_id)
                .select_related("contestant")
                .annotate(contestant_name=F("contestant__name"))
                .order_by("-start_time")
            )

            paginated_sessions = self.paginate_queryset(sessions, request, view=self)
            if not paginated_sessions:
                return Response(
                    {"message": "No sessions found for the specified game."},
                    status=status.HTTP_200_OK,
                )

            session_data = [
                {
                    "id": str(session.id),
                    "contestant_id": str(session.contestant_id),
                    "contestant_name": session.contestant_name,
                    "start_time": session.start_time,
                    "end_time": session.end_time,
                    "score": session.score,
                }
                for session in paginated_sessions
            ]

            return self.get_paginated_response(session_data)

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
