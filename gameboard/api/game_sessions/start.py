from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from django.db import IntegrityError

from gameboard.games.models import Game, Contestant, GameSession


class StartGameSessionView(APIView):
    """
    API to start a game session for a contestant.
    """

    def post(self, request):
        game_id = request.data.get("game_id")
        contestant_id = request.data.get("contestant_id")

        if not game_id or not contestant_id:
            return Response(
                {"error": "Both 'game_id' and 'contestant_id' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response(
                {"error": f"Game with id '{game_id}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            contestant = Contestant.objects.get(id=contestant_id)
            if not contestant.is_active:
                return Response(
                    {"error": f"Contestant '{contestant.name}' is not active."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Contestant.DoesNotExist:
            return Response(
                {"error": f"Contestant with id '{contestant_id}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if contestant already has an ongoing session in this game
        ongoing_session = GameSession.objects.filter(
            game=game,
            contestant=contestant,
            end_time__isnull=True,
        ).exists()

        if ongoing_session:
            return Response(
                {
                    "error": f"Contestant '{contestant.name}' already has an ongoing session in game '{game.name}'."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = GameSession.objects.create(
                game=game, contestant=contestant, start_time=now()
            )
        except IntegrityError as e:
            return Response(
                {"error": f"Failed to create game session: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": "Game session started successfully.",
                "session_id": session.id,
                "contestant": contestant.name,
                "game": game.name,
                "start_time": session.start_time,
            },
            status=status.HTTP_201_CREATED,
        )
