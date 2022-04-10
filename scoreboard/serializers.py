from rest_framework import serializers

from .models import Game, Match, MatchStatus, Player, Point


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['player', 'score']


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['player', 'set', 'games_won']


class MatchStatusSerializer(serializers.ModelSerializer):
    match_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MatchStatus
        fields = ['current_set', 'tiebreaker_active', 'latest_event', 'winner', 'match_id']
