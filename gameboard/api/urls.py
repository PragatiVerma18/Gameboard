from django.urls import path, include

from .contestants import urls as contestants_urls
from .games import urls as games_urls
from .game_sessions import urls as game_sessions_urls
from .leaderboard import urls as leaderboard_urls

urlpatterns = [
    path("games/", include(games_urls)),
    path("contestants/", include(contestants_urls)),
    path("leaderboard/", include(leaderboard_urls)),
    path("game-sessions/", include(game_sessions_urls)),
]
