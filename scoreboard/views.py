from rest_framework import generics, viewsets
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


class PointUpdateView(generics.UpdateAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer

    # TODO: Score calculation
