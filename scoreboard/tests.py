from django.test import TestCase
from rest_framework import status

from .models import Match, Player


class MatchTestCase(TestCase):
    def setUp(self):
        self.player1 = Player.objects.create(name='Player1')
        self.player2 = Player.objects.create(name='Player2')
        self.match1 = Match.objects.create(players=[self.player1, self.player2])

    def test_create_match(self):
        data = {
            'sets': 3,
            'players': [self.player1.id, self.player2.id],
        }
        response = self.client.post(
            '/scoreboard/matches/',
            data=data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertResponseOk(response, contains=data)

    def test_add_player_point(self):
        response = self.client.post(
            f'/scoreboard/points/{self.match1.id}/{self.player1.id}/',
            format='json',
        )
        data = {'success': True}
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertResponseOk(response, contains=data)
