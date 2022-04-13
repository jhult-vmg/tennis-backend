from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from rest_framework import serializers


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
    latest_event = models.CharField(default='Match Started', max_length=120, null=True, blank=True)

    def __str__(self):
        return f'MatchStatus ({self.pk})'


class Point(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    score = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0, 'Love is the least expected minimum'),
            MaxValueValidator(4, 'Score cannot exceed 4')
        ]
    )

    class Meta:
        unique_together = ('match', 'player')

    def __str__(self):
        return f'Point ({self.pk})'

    def save(self, *args, **kwargs):
        if self.player not in self.match.players.all():
            raise ValidationError('Player does not belong to the match!')
        try:
            match_status = MatchStatus.objects.get(match_id=self.match)
        except MatchStatus.DoesNotExist:
            # on creating new match
            match_status = None
        if match_status and match_status.winner:
            raise ValidationError('Cannot add point. Match is finished already!')

        super(Point, self).save(*args, **kwargs)


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

    class Meta:
        unique_together = ('match', 'player', 'set')

    def __str__(self):
        return f'Game ({self.pk})'


@receiver(post_save, sender=Match)
def init_match_status(sender, instance, **kwargs):
    # Create match status record
    MatchStatus.objects.create(match=instance, current_set=1)


def match_players_added(sender, instance, action, **kwargs):
    # Validate player count
    if action == 'pre_add':
        no_players = len(kwargs['pk_set'])
        if no_players != 2:
            raise serializers.ValidationError({
                'players': 'Invalid number of players. Two players(teams) are required!'
            })

    if action == 'post_add':
        # Initialize points record for players
        for player in instance.players.all():
            Point.objects.create(match=instance, player=player, score=0)


m2m_changed.connect(match_players_added, sender=Match.players.through)
