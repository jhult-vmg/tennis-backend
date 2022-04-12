from django.urls import path
from rest_framework import routers

from .views import (MatchViewset, PlayerViewset, PointUpdateView,
                    ScoreCorrectionView)

router = routers.SimpleRouter()
router.register('players', PlayerViewset, basename='player')
router.register('matches', MatchViewset, basename='match')

urlpatterns = [
    path('points/<int:match>/<int:player>/', PointUpdateView.as_view(), name='point'),
    path('scores/<int:match>/<int:player>/', ScoreCorrectionView.as_view(), name='score-correction'),
]

urlpatterns += router.urls
