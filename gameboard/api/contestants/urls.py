from django.urls import path

from .create import CreateContestantView
from .delete import DeleteContestantView
from .details import ContestantDetailView
from .list_sessions import ContestantSessionsListView
from .list import ContestantListView
from .update import UpdateContestantView

urlpatterns = [
    path("", ContestantListView.as_view(), name="list-contestants"),
    path("create/", CreateContestantView.as_view(), name="create-contestant"),
    path(
        "<uuid:contestant_id>/",
        ContestantDetailView.as_view(),
        name="contestant-details",
    ),
    path(
        "<uuid:contestant_id>/update/",
        UpdateContestantView.as_view(),
        name="update-contestant",
    ),
    path(
        "<uuid:contestant_id>/delete/",
        DeleteContestantView.as_view(),
        name="delete-contestant",
    ),
    path(
        "<uuid:contestant_id>/sessions/",
        ContestantSessionsListView.as_view(),
        name="list-contestant-sessions",
    ),
]
