from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.utils.timezone import now
from django.db import transaction

from gameboard.games.models import Game, GameSession


class DeleteGameView(APIView):
    """
    API to delete a game (soft delete by setting is_active=False).
    Also ends all ongoing sessions for this game in a transaction.
    """

    def post(self, request, game_id):
        try:
            game = Game.objects.filter(id=game_id).first()

            if not game:
                return Response(
                    {"error": "Game not found."}, status=status.HTTP_404_NOT_FOUND
                )

            if not game.is_active:
                return Response(
                    {"error": "Game is already deleted."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                game.is_active = False
                game.save()

                # End all ongoing game sessions
                GameSession.objects.filter(game=game, end_time__isnull=True).update(
                    end_time=now()
                )

            return Response(
                {"message": f"Game '{game.name}' has been deleted."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
