from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from gameboard.games.models import GameSession, Contestant


class ContestantSessionsListView(APIView, PageNumberPagination):
    """
    API to list game sessions for a specific contestant with pagination and filtering.
    """

    page_size = 10

    def get(self, request, contestant_id):
        try:
            contestant = Contestant.objects.filter(id=contestant_id).first()
            if not contestant:
                return Response(
                    {"error": "Contestant not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Optional date filter (e.g., ?date=2025-02-09)
            date_filter = request.GET.get("date")
            sessions = GameSession.objects.filter(contestant_id=contestant_id)

            if date_filter:
                sessions = sessions.filter(
                    Q(start_time__date=date_filter) | Q(end_time__date=date_filter)
                )

            sessions = (
                sessions.select_related("game")
                .only("id", "game__name", "start_time", "end_time", "score")
                .order_by("-start_time")
            )

            result_page = self.paginate_queryset(sessions, request, view=self)

            data = [
                {
                    "id": str(session.id),
                    "game_name": session.game.name,
                    "start_time": session.start_time,
                    "end_time": session.end_time,
                    "score": session.score,
                }
                for session in result_page
            ]

            return self.get_paginated_response(data)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
