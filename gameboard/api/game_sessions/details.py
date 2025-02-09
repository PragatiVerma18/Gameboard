from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers

from django.core.exceptions import ObjectDoesNotExist

from gameboard.games.models import GameSession


class GameSessionSerializer(serializers.ModelSerializer):
    game_name = serializers.CharField(source="game.name", read_only=True)
    contestant_name = serializers.CharField(source="contestant.name", read_only=True)

    class Meta:
        model = GameSession
        fields = [
            "id",
            "game",
            "game_name",
            "contestant",
            "contestant_name",
            "start_time",
            "end_time",
            "score",
        ]


class GameSessionDetailsView(APIView):
    """
    API to get details of a specific game session.
    """

    def get(self, request, session_id):
        try:
            session = GameSession.objects.select_related("game", "contestant").get(
                id=session_id
            )
            serializer = GameSessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {"error": "Game session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
