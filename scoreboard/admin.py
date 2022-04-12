from django.contrib import admin

from .models import Game, Match, MatchStatus, Player, Point

admin.site.register(Player)
admin.site.register(Match)
admin.site.register(MatchStatus)
admin.site.register(Point)
admin.site.register(Game)
