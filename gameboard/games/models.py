from django.db import models
from django.utils.dateformat import format

from gameboard.common.db.models import AuditDates, UUIDAsPrimaryKey


class Contestant(AuditDates, UUIDAsPrimaryKey):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.joined_at:
            self.joined_at = (
                self.created_at
            )  # Default to creation time if not manually set
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Game(AuditDates, UUIDAsPrimaryKey):
    name = models.CharField(max_length=255)
    upvotes = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class GameSession(AuditDates, UUIDAsPrimaryKey):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.game.name} - {self.contestant.name} ({self.start_time})"


class GamePopularity(AuditDates, UUIDAsPrimaryKey):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateField()
    popularity_score = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        date_str = format(self.date, "N j, Y")
        return f"{self.game.name} - {date_str}"
