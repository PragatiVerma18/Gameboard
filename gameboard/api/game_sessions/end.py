from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.utils.timezone import now
from django.db import transaction

from gameboard.games.models import GameSession


class EndGameSessionView(APIView):
    """
    API to end an active game session for a contestant and save the final score.
    """

    def post(self, request):
        session_id = request.data.get("session_id")
        final_score = request.data.get("score")

        if not session_id:
            return Response(
                {"error": "'session_id' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if final_score is None or not isinstance(final_score, int):
            return Response(
                {"error": "'score' is required and must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                session = GameSession.objects.select_for_update().get(
                    id=session_id, end_time__isnull=True
                )
                session.end_time = now()
                session.score = final_score
                session.save()
        except GameSession.DoesNotExist:
            return Response(
                {"error": f"No active session found with id '{session_id}'."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": "Game session ended successfully.",
                "session_id": session.id,
                "contestant": session.contestant.name,
                "game": session.game.name,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "final_score": session.score,
            },
            status=status.HTTP_200_OK,
        )
