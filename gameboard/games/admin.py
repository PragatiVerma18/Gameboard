from django.contrib import admin
from .models import Contestant, Game, GameSession, GamePopularity

from gameboard.common.admin.utils import (
    BaseModelAdmin,
    datetime_format_ist,
    object_link,
)


@admin.register(Contestant)
class ContestantAdmin(BaseModelAdmin):

    def joined_at_ist(self: GameSession):
        return datetime_format_ist(self.joined_at)

    joined_at_ist.admin_order_field = "joined_at"

    list_display = [
        "truncated_id",
        "name",
        "is_active",
        joined_at_ist,
    ]
    list_filter = ("is_active", "joined_at")
    search_fields = [
        "id",
        "name",
    ]


@admin.register(Game)
class GameAdmin(BaseModelAdmin):
    list_display = [
        "truncated_id",
        "name",
        "upvotes",
    ]
    list_filter = ("upvotes",)
    search_fields = ("name",)


@admin.register(GameSession)
class GameSessionAdmin(BaseModelAdmin):

    def game(self: GameSession):
        return object_link(self.game, display_value=self.game.name)

    def contestant(self: GameSession):
        return object_link(self.contestant, display_value=self.contestant.name)

    def start_time_ist(self: GameSession):
        return datetime_format_ist(self.start_time)

    start_time_ist.admin_order_field = "start_time"

    def end_time_ist(self: GameSession):
        return datetime_format_ist(self.end_time)

    end_time_ist.admin_order_field = "end_time"

    list_display = [
        "truncated_id",
        game,
        contestant,
        "start_time",
        "end_time",
        "score",
    ]
    search_fields = [
        "id",
        "game__id",
        "game__name",
        "contestant__id",
        "contestant__name",
    ]
    ordering = ("start_time",)
    list_select_related = [
        "game",
        "contestant",
    ]
    raw_id_fields = ["game", "contestant"]


@admin.register(GamePopularity)
class GamePopularityAdmin(BaseModelAdmin):

    def game(self: GamePopularity):
        return object_link(self.game, display_value=self.game.name)

    def last_updated_ist(self: GamePopularity):
        return datetime_format_ist(self.last_updated)

    list_display = [
        "truncated_id",
        game,
        "date",
        "popularity_score",
        last_updated_ist,
    ]
    search_fields = [
        "id",
        "game__id",
        "game__name",
    ]
    ordering = ("date",)
