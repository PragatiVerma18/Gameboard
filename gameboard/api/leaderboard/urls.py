from django.urls import path

from .global_leaderboard import GlobalLeaderboardView
from .game_leaderboard import GameLeaderboardView
from .date_level_leaderboard import (
    DateLeaderboardView,
)

urlpatterns = [
    path("", GlobalLeaderboardView.as_view(), name="global-leaderboard"),
    path(
        "game/<uuid:game_id>/", GameLeaderboardView.as_view(), name="game-leaderboard"
    ),
    path("date/", DateLeaderboardView.as_view(), name="date-leaderboard"),
]
