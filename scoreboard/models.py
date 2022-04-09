from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class SetChoice(models.IntegerChoices):
    THREE_SET = 3
    FIVE_SET = 5


class Player(models.Model):
    name = models.CharField(default='Player', max_length=30)

    def __str__(self):
        return f'{self.name} ({self.pk})'


class Match(models.Model):
    players = models.ManyToManyField(Player)
    sets = models.PositiveIntegerField(choices=SetChoice.choices, default=SetChoice.THREE_SET)

    def __str__(self):
        return f'Match ({self.pk})'


class MatchStatus(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    current_set = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, 'Current set should be atleast 1'),
            MaxValueValidator(5, 'Current set should not exceed 5')
        ]
    )
    tiebreaker_active = models.BooleanField(default=False)
    winner = models.ForeignKey(Player, on_delete=models.PROTECT, null=True)
    latest_event = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return f'MatchStatus ({self.pk})'


class Point(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    score = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0, 'Love is the least expected minimum'),
            MaxValueValidator(4, 'Score cannot exceed 5')
        ]
    )

    def __str__(self):
        return f'Point ({self.pk})'


class Game(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    set = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, 'Set should be atleast 1'),
            MaxValueValidator(5, 'Set should not exceed 5')
        ]
    )
    games_won = models.PositiveIntegerField()

    def __str__(self):
        return f'Game ({self.pk})'
