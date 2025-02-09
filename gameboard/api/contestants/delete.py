from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from gameboard.games.models import Contestant


class DeleteContestantView(APIView):
    def post(self, request, contestant_id, *args, **kwargs):
        try:
            contestant = Contestant.objects.get(id=contestant_id)
            contestant.is_active = False
            contestant.save()
            return Response(
                {"message": "Contestant marked as inactive."}, status=status.HTTP_200_OK
            )
        except Contestant.DoesNotExist:
            return Response(
                {"error": "Contestant not found."}, status=status.HTTP_404_NOT_FOUND
            )
