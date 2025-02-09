from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from gameboard.games.models import Contestant


class UpdateContestantView(APIView):
    """
    API to update a contestant's name.
    Only allows PATCH requests.
    """

    def patch(self, request, contestant_id):
        try:
            contestant = get_object_or_404(Contestant, id=contestant_id)

            new_name = request.data.get("name")
            if not new_name:
                return Response(
                    {"error": "Name is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            contestant.name = new_name
            contestant.save()

            return Response(
                {"message": "Contestant updated successfully", "name": contestant.name},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
