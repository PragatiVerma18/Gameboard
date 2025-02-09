from datetime import timedelta
import logging

from celery import shared_task

from django.core.cache import cache
from django.db.models import Max, Count
from django.utils import timezone

from gameboard.games.models import Game, GameSession, GamePopularity

# Set up logging
logger = logging.getLogger(__name__)

"""
Create a popularity score of a game based on:
- Number of people who played the game yesterday: w1
- Number of people playing the game right now: w2
- Total number of upvotes received for the game: w3
- Maximum session length of the game played (consider only the sessions played yesterday): w4
- Total number of sessions played yesterday: w5
"""


def calculate_n_daily_players(game, date):
    return (
        GameSession.objects.filter(game=game, start_time__date=date)
        .values("contestant")
        .distinct()
        .count()
    )


def calculate_n_current_players(game):
    return (
        GameSession.objects.filter(game=game, end_time__isnull=True)
        .values("contestant")
        .distinct()
        .count()
    )


def calculate_n_upvotes(game):
    return game.upvotes


def calculate_max_session_length_for_game(game, date):
    session_length = GameSession.objects.filter(
        game=game, start_time__date=date
    ).annotate(session_length=Max("end_time") - Max("start_time")).aggregate(
        Max("session_length")
    )[
        "session_length__max"
    ] or timedelta(
        seconds=0
    )
    return session_length.total_seconds()


def calculate_n_daily_sessions(game, date):
    return GameSession.objects.filter(game=game, start_time__date=date).count()


@shared_task
def cache_popularity_factors_and_max_values():
    """
    Task to cache non-changing game popularity factors (n_daily_players, max_session_length_for_game, n_daily_sessions)
    and maximum values for normalization.
    Runs once per day (every 24 hours).
    """
    logger.info("Running cache_popularity_factors_and_max_values task")
    yesterday = timezone.now().date() - timedelta(days=1)

    popularity_cache = {}

    for game in Game.objects.all():
        n_daily_players = calculate_n_daily_players(game, yesterday)
        max_session_length_for_game = calculate_max_session_length_for_game(
            game, yesterday
        )
        n_daily_sessions = calculate_n_daily_sessions(game, yesterday)

        popularity_cache[f"game_{game.id}_n_daily_players"] = n_daily_players
        popularity_cache[f"game_{game.id}_max_session_length_for_game"] = (
            max_session_length_for_game
        )
        popularity_cache[f"game_{game.id}_n_daily_sessions"] = n_daily_sessions

    # Calculate max values for normalization across all games
    max_daily_players = (
        GameSession.objects.filter(start_time__date=yesterday)
        .values("game")
        .annotate(count=Count("contestant", distinct=True))
        .aggregate(Max("count"))["count__max"]
        or 1
    )

    max_concurrent_players = (
        GameSession.objects.filter(end_time__isnull=True)
        .values("game")
        .annotate(count=Count("contestant", distinct=True))
        .aggregate(Max("count"))["count__max"]
        or 1
    )

    max_upvotes = Game.objects.aggregate(Max("upvotes"))["upvotes__max"] or 1

    max_session_length_across_all_games = GameSession.objects.filter(
        start_time__date=yesterday
    ).annotate(session_length=Max("end_time") - Max("start_time")).aggregate(
        Max("session_length")
    )[
        "session_length__max"
    ] or timedelta(
        seconds=1
    )
    max_session_length_across_all_games = (
        max_session_length_across_all_games.total_seconds()
    )

    max_daily_sessions = (
        GameSession.objects.filter(start_time__date=yesterday)
        .values("game")
        .annotate(count=Count("id"))
        .aggregate(Max("count"))["count__max"]
        or 1
    )

    max_values_cache = {
        "max_daily_players": max_daily_players,
        "max_concurrent_players": max_concurrent_players,
        "max_upvotes": max_upvotes,
        "max_session_length_across_all_games": max_session_length_across_all_games,
        "max_daily_sessions": max_daily_sessions,
    }

    # Store all cached values with a timeout of 24 hours (86,400 seconds)
    cache.set_many({**popularity_cache, **max_values_cache}, timeout=86400)
    logger.info("Finished running cache_popularity_factors_and_max_values task")
    logger.info("Finished running cache_popularity_factors_and_max_values task")
    logger.info(f"Set cache for max_daily_players: {max_daily_players}")
    logger.info(f"Set cache for max_concurrent_players: {max_concurrent_players}")
    logger.info(f"Set cache for max_upvotes: {max_upvotes}")
    logger.info(
        f"Set cache for max_session_length_across_all_games: {max_session_length_across_all_games}"
    )
    logger.info(f"Set cache for max_daily_sessions: {max_daily_sessions}")


@shared_task
def refresh_game_popularity():
    """
    Task to refresh game popularity scores every 5 minutes.
    Uses cached values for non-changing parameters.
    """
    logger.info("Running refresh_game_popularity task")
    now = timezone.now()
    yesterday = now.date() - timedelta(days=1)

    popularity_updates = {}

    for game in Game.objects.all():
        # Get cached values or calculate if cache miss
        n_daily_players = cache.get(f"game_{game.id}_n_daily_players")
        if n_daily_players is None:
            n_daily_players = calculate_n_daily_players(game, yesterday)
            cache.set(f"game_{game.id}_n_daily_players", n_daily_players, timeout=86400)

        max_session_length_for_game = cache.get(
            f"game_{game.id}_max_session_length_for_game"
        )
        if max_session_length_for_game is None:
            max_session_length_for_game = calculate_max_session_length_for_game(
                game, yesterday
            )
            cache.set(
                f"game_{game.id}_max_session_length_for_game",
                max_session_length_for_game,
                timeout=86400,
            )

        n_daily_sessions = cache.get(f"game_{game.id}_n_daily_sessions")
        if n_daily_sessions is None:
            n_daily_sessions = calculate_n_daily_sessions(game, yesterday)
            cache.set(
                f"game_{game.id}_n_daily_sessions", n_daily_sessions, timeout=86400
            )

        # Compute dynamic values
        n_current_players = calculate_n_current_players(game)
        n_upvotes = calculate_n_upvotes(game)

        # Calculate max values for normalization
        max_daily_players = cache.get("max_daily_players", 1)
        max_concurrent_players = cache.get("max_concurrent_players", 1)
        max_upvotes = cache.get("max_upvotes", 1)
        max_session_length_across_all_games = cache.get(
            "max_session_length_across_all_games", 1
        )
        max_daily_sessions = cache.get("max_daily_sessions", 1)

        # Avoid division by zero
        max_daily_players = max(max_daily_players, 1)
        max_concurrent_players = max(max_concurrent_players, 1)
        max_upvotes = max(max_upvotes, 1)
        max_session_length_across_all_games = max(
            max_session_length_across_all_games, 1
        )
        max_daily_sessions = max(max_daily_sessions, 1)

        # Calculate popularity score and round to two decimal points
        score = round(
            (0.3 * (n_daily_players / max_daily_players))
            + (0.2 * (n_current_players / max_concurrent_players))
            + (0.25 * (n_upvotes / max_upvotes))
            + (
                0.15
                * (max_session_length_for_game / max_session_length_across_all_games)
            )
            + (0.1 * (n_daily_sessions / max_daily_sessions)),
            2,
        )

        GamePopularity.objects.update_or_create(
            game=game,
            date=now.date(),
            defaults={"popularity_score": score, "last_updated": now},
        )

        popularity_updates[f"game_{game.id}_score"] = score

    cache.set_many(popularity_updates, timeout=300)  # Cache scores for 5 minutes
    logger.info("Finished running refresh_game_popularity task")
