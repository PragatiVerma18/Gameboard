from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.pagination import PageNumberPagination

from gameboard.games.models import Game


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["id", "name", "upvotes"]


class ListGamesView(APIView, PageNumberPagination):
    """
    API to list all active games with pagination.
    """

    page_size = 10

    def get(self, request):
        try:
            games = (
                Game.objects.filter(is_active=True)
                .only("id", "name", "upvotes")
                .order_by("-upvotes")
            )

            paginated_games = self.paginate_queryset(games, request, view=self)
            serializer = GameSerializer(paginated_games, many=True)

            return self.get_paginated_response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
