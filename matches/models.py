from django.db import models
from players.models import Player

class Match(models.Model):
    date = models.DateField()
    competition = models.CharField(max_length=80, blank=True)
    opponent = models.CharField(max_length=80)
    home_away = models.CharField(max_length=5, choices=[("H","Home"),("A","Away")])
    result = models.CharField(max_length=10, blank=True)

    def __str__(self):
        side = "H" if self.home_away == "H" else "A"
        return f"{self.date} vs {self.opponent} ({side})"

class Appearance(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    minutes = models.PositiveIntegerField(default=0)
    goals = models.PositiveIntegerField(default=0)
    yellow = models.PositiveIntegerField(default=0)
    red = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("match", "player")
