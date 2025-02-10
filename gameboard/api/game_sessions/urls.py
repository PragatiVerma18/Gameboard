from django.urls import path

from .start import StartGameSessionView
from .end import EndGameSessionView
from .details import GameSessionDetailsView

urlpatterns = [
    path(
        "start/",
        StartGameSessionView.as_view(),
        name="start-game-session",
    ),
    path("end/", EndGameSessionView.as_view(), name="end-game-session"),
    path(
        "<uuid:session_id>/",
        GameSessionDetailsView.as_view(),
        name="game-session-details",
    ),
]
