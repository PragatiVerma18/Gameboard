from django.urls import path

from .create import CreateGameView
from .delete import DeleteGameView
from .details import GameDetailsView
from .list import ListGamesView
from .upvote import UpvoteGameView
from .list_sessions import ListGameSessionsView

urlpatterns = [
    path("", ListGamesView.as_view(), name="list-games"),
    path("create/", CreateGameView.as_view(), name="create-game"),
    path("<uuid:game_id>/", GameDetailsView.as_view(), name="game-details"),
    path("<uuid:game_id>/delete/", DeleteGameView.as_view(), name="delete-game"),
    path("<uuid:game_id>/upvote/", UpvoteGameView.as_view(), name="upvote-game"),
    path(
        "<uuid:game_id>/sessions/",
        ListGameSessionsView.as_view(),
        name="list-game-sessions",
    ),
]
