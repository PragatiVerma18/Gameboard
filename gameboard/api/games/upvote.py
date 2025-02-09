from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction

from gameboard.games.models import Game


class UpvoteGameView(APIView):
    """
    API to upvote a game.
    """

    def post(self, request, game_id):
        try:
            with transaction.atomic():
                game = (
                    Game.objects.filter(id=game_id, is_active=True)
                    .select_for_update()
                    .first()
                )

                if not game:
                    return Response(
                        {"error": "Game not found or inactive."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                game.upvotes = game.upvotes + 1
                game.save(update_fields=["upvotes"])

            return Response(
                {"message": f"Upvoted game '{game.name}'.", "upvotes": game.upvotes},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
