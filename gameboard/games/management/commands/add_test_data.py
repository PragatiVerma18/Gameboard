import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware

from gameboard.games.models import Contestant, Game, GameSession


class Command(BaseCommand):
    help = "Populate the database with test data for games, contestants, and sessions"

    def handle(self, *args, **kwargs):
        self.create_games()
        self.create_contestants()
        self.create_game_sessions()

    def create_games(self):
        self.games = []
        game_names = ["Chess", "Poker", "Tetris", "Fortnite", "Call of Duty"]
        for name in game_names:
            game = Game.objects.create(name=name, upvotes=random.randint(10, 100))
            self.games.append(game)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(self.games)} games"))

    def create_contestants(self):
        self.contestants = []
        base_time = make_aware(datetime.now() - timedelta(days=3))

        for i in range(10):  # Creating 10 contestants
            join_time = base_time + timedelta(hours=random.randint(0, 48))
            contestant = Contestant.objects.create(
                name=f"Player_{i+1}", is_active=True, joined_at=join_time
            )
            self.contestants.append(contestant)

        self.stdout.write(
            self.style.SUCCESS(f"✅ Created {len(self.contestants)} contestants")
        )

    def create_game_sessions(self):
        base_time = make_aware(datetime.now() - timedelta(days=1))
        for contestant in self.contestants:
            game = random.choice(self.games)
            start_time = base_time + timedelta(minutes=random.randint(0, 300))
            end_time = start_time + timedelta(minutes=random.randint(10, 60))

            GameSession.objects.create(
                game=game,
                contestant=contestant,
                start_time=start_time,
                end_time=end_time,
                score=random.randint(10, 100),
            )

        self.stdout.write(self.style.SUCCESS("✅ Created game sessions with scores"))
