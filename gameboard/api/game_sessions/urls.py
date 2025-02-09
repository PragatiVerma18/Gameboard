from django.urls import path

from .start import StartGameSessionView
from .end import EndGameSessionView
from .details import GameSessionDetailsView

urlpatterns = [
    path(
        "start/<uuid:game_id>/",
        StartGameSessionView.as_view(),
        name="start-game-session",
    ),
    path("end/<uuid:game_id>/", EndGameSessionView.as_view(), name="end-game-session"),
    path(
        "details/<uuid:session_id>/",
        GameSessionDetailsView.as_view(),
        name="game-session-details",
    ),
]
