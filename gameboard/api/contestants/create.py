from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils import timezone

from gameboard.games.models import Contestant


class ContestantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contestant
        fields = ["name"]

    def validate(self, data):
        if "name" not in data:
            raise serializers.ValidationError({"name": "This field is required."})
        return data


class CreateContestantView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ContestantSerializer(data=request.data)

        if serializer.is_valid():
            contestant = Contestant(
                name=serializer.validated_data["name"],
                joined_at=timezone.now(),
                is_active=True,
            )
            contestant.save()
            return Response(
                data=ContestantSerializer(contestant).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
