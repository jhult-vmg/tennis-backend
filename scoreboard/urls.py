from django.urls import path
from rest_framework import routers

from .views import MatchViewset, PlayerViewset, PointUpdateView

router = routers.SimpleRouter()
router.register('players', PlayerViewset, basename='player')
router.register('matches', MatchViewset, basename='match')

urlpatterns = [
    path('matches/<int:match>/<int:player>/points/', PointUpdateView.as_view(), name='point'),
]

urlpatterns += router.urls
