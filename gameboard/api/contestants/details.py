from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Prefetch

from gameboard.games.models import Contestant, GameSession, Game


class ContestantDetailView(APIView):
    """
    Optimized API to fetch details of a contestant, including their game sessions and total score.
    """

    def get(self, request, contestant_id):
        try:
            contestant = (
                Contestant.objects.annotate(total_score=Sum("gamesession__score"))
                .prefetch_related(
                    Prefetch(
                        "gamesession_set",
                        queryset=GameSession.objects.select_related("game").only(
                            "game__name", "score", "start_time", "end_time"
                        ),
                    )
                )
                .get(id=contestant_id)
            )

            game_sessions = [
                {
                    "id": str(session.id),
                    "game_name": session.game.name,
                    "score": session.score,
                    "start_time": session.start_time,
                    "end_time": session.end_time,
                }
                for session in contestant.gamesession_set.all()
            ]

            data = {
                "id": str(contestant.id),
                "name": contestant.name,
                "is_active": contestant.is_active,
                "joined_at": contestant.joined_at,
                "total_score": contestant.total_score or 0,
                "game_sessions": game_sessions,
            }

            return Response(data, status=status.HTTP_200_OK)

        except Contestant.DoesNotExist:
            return Response(
                {"error": "Contestant not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
