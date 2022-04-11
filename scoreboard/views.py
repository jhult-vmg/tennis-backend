from django.db.models import Sum
from rest_framework import exceptions, generics, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Game, Match, MatchStatus, Player, Point
from .serializers import (GameSerializer, MatchSerializer,
                          MatchStatusSerializer, PlayerSerializer,
                          PointSerializer)


class PlayerViewset(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class MatchViewset(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    @action(detail=True, methods=['get'],)
    def info(self, request, pk=None):
        """
        Returns the current status, points and player games won
        for the match that is given
        """
        match_status = get_object_or_404(MatchStatus.objects.all(), match_id=pk)
        points = Point.objects.filter(match_id=pk)
        games = Game.objects.filter(match_id=pk)

        match_status_serializer = MatchStatusSerializer(match_status)
        points_serializer = PointSerializer(points, many=True)
        games_serializer = GameSerializer(games, many=True)

        return Response({
            **match_status_serializer.data,
            'points': points_serializer.data,
            'games': games_serializer.data
        })


class PointUpdateView(generics.GenericAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    lookup_fields = ('match', 'player')

    def get_object(self):
        queryset = self.get_queryset()
        filter = {}
        for field in self.lookup_fields:
            filter[field] = self.kwargs[field]

        obj = get_object_or_404(queryset, **filter)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_opponent_score(self):
        qs = Point.objects.filter(match_id=self.kwargs['match']).exclude(player_id=self.kwargs['player'])
        if (qs):
            return qs.first()
        else:
            raise exceptions.ValidationError('Unable to find opponent points')

    def get_match(self):
        queryset = Match.objects.all()
        filter = {}
        filter['id'] = self.kwargs['match']
        obj = get_object_or_404(queryset, **filter)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_match_status(self):
        queryset = MatchStatus.objects.all()
        filter = {}
        filter['match'] = self.kwargs['match']
        obj = get_object_or_404(queryset, **filter)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_match_players(self, match):
        """
        Finds player and opponent based on serve
        """
        player = match.players.all().filter(pk=self.kwargs['player']).get()
        opponent = match.players.all().exclude(pk=self.kwargs['player']).get()
        return player, opponent

    def update_player_score(self, player, new_score):
        """
        Update player score based last serve outcome
        """
        match = self.get_match()
        return Point.objects.filter(match=match, player=player).update(score=new_score)

    def get_or_create_game(self, match, player, set):
        """
        Create Game record if not exists
        """
        try:
            Game.objects.get(match=match, player=player, set=set)
        except Game.DoesNotExist:
            Game.objects.create(match=match, player=player, set=set, games_won=0)

    def init_game(self):
        """
        Initialize Game win record for players
        """
        match = self.get_match()
        match_status = self.get_match_status()
        player, opponent = self.get_match_players(match)
        self.get_or_create_game(match, player, match_status.current_set)
        self.get_or_create_game(match, opponent, match_status.current_set)

    def game_won(self, player):
        """
        Update player games won
        """
        match = self.get_match()
        match_status = self.get_match_status()

        try:
            obj = Game.objects.get(match=match, player=player, set=match_status.current_set)
            obj.games_won += 1
            obj.save()

        except Game.DoesNotExist:
            Game.objects.create(match=match, player=player, set=match_status.current_set, games_won=1)

    def reset_score(self):
        """
        Reset score for new game
        """
        Point.objects.filter(match_id=self.kwargs['match']).update(score=0)

    def next_set(self):
        """
        Progress match to the next set
        """
        match_status = self.get_match_status()
        match_status.current_set += 1
        match_status.save()

    def match_won(self, player):
        """
        Add player as winner
        """
        match_status = self.get_match_status()
        match_status.winner = player
        match_status.save()

    def announce_event(self, message):
        """
        Log latest event
        """
        match_status = self.get_match_status()
        match_status.latest_event = message
        match_status.save()

    def put(self, request, *args, **kwargs):
        """
        Process match progress by processing each score made by a player
        The point system assumed is as follows:
            0 points = Love
            1 point = 15
            2 points = 30
            3 points = 40
            Tied score = All
            40-40 = Deuce
            Server wins deuce point = Ad-In
            Receiver wins deuce point = Ad-Out
        """
        match = self.get_match()
        match_status = self.get_match_status()
        player, opponent = self.get_match_players(match)
        self.init_game()

        # Read previous scores of the players
        player_score_previous = self.get_object().score
        opponent_score = self.get_opponent_score().score

        # Look for Ad-Out
        DUECE_SCORE = 3
        AD_IN_SCORE = 4
        ad_out = player_score_previous == DUECE_SCORE and opponent_score == AD_IN_SCORE
        if ad_out:
            # opponent looses 1 point
            self.update_player_score(opponent, opponent_score-1)
            player_score_now = player_score_previous

        else:
            # Add point to prev score
            player_score_now = player_score_previous + 1

        # Draw game winner - Is player ahead four points ?
        ahead_four_points = player_score_now == 5

        if ahead_four_points:
            self.game_won(player)  # Player won the game
            self.announce_event(f'{player.name} won the game')
            self.reset_score()

            # Find games won in current set for player and opponent
            player_games_won_currentset = Game.objects.get(
                    match=match, player=player, set=match_status.current_set
                ).games_won

            opponent_games_won_currentset = Game.objects.get(
                    match=match, player=opponent, set=match_status.current_set
                ).games_won

            # Advantage set rule
            """
            In an advantage set, a player or team needs to win six games, by two, to win the set.
            This means that there is no tiebreak game played at 6-6.
            The set continues until one player/team wins by two games.
            """

            player_won_set = player_games_won_currentset >= 6 \
                and player_games_won_currentset - opponent_games_won_currentset >= 2
            if player_won_set:
                # player won set, move to next set
                if match_status.current_set < match.sets:
                    self.next_set()
                else:
                    # All sets finished, now draw match

                    # Find games won in All sets for the player and opponent
                    player_games_won_allsets = Game.objects.filter(
                            match=match, player=player
                        ).aggregate(Sum('games_won'))['games_won__sum']

                    opponent_games_won_allsets = Game.objects.filter(
                            match=match, player=opponent
                        ).aggregate(Sum('games_won'))['games_won__sum']

                    winner = player if player_games_won_allsets > opponent_games_won_allsets else opponent
                    self.match_won(winner)
                    self.announce_event(f'{winner.name} won the match!')

        else:
            # Update player score, game continues
            self.update_player_score(player, player_score_now)
            self.announce_event(f'{player.name} scored the point')

        return Response({'success': True}, status=200)
