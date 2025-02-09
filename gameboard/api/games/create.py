from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers

from gameboard.games.models import Game


class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["name"]

    def validate_name(self, value):
        if Game.objects.filter(name=value).exists():
            raise serializers.ValidationError("A game with this name already exists.")
        return value


class CreateGameView(APIView):
    """
    API to create a new game.
    """

    def post(self, request):
        serializer = CreateGameSerializer(data=request.data)
        if serializer.is_valid():
            try:
                game = serializer.save()
                return Response(
                    {"id": game.id, "name": game.name}, status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
