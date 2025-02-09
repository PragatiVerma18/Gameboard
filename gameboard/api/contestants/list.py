from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum

from gameboard.games.models import Contestant


class ContestantListView(APIView, PageNumberPagination):
    """
    API to list contestants with pagination, total scores, and optional search.
    """

    page_size = 10

    def get(self, request):
        try:
            search_query = request.GET.get("search", "").strip()

            contestants = (
                Contestant.objects.annotate(total_score=Sum("gamesession__score"))
                .only("id", "name", "is_active", "joined_at")
                .order_by("-total_score", "name")
            )

            if search_query:
                contestants = contestants.filter(name__icontains=search_query)

            result_page = self.paginate_queryset(contestants, request, view=self)

            data = [
                {
                    "id": str(contestant.id),
                    "name": contestant.name,
                    "is_active": contestant.is_active,
                    "joined_at": contestant.joined_at,
                    "total_score": contestant.total_score or 0,
                }
                for contestant in result_page
            ]

            return self.get_paginated_response(data)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
