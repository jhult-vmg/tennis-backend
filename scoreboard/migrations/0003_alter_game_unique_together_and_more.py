# Generated by Django 4.0.3 on 2022-04-12 22:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scoreboard', '0002_alter_matchstatus_latest_event_alter_point_score'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='game',
            unique_together={('match', 'player', 'set')},
        ),
        migrations.AlterUniqueTogether(
            name='point',
            unique_together={('match', 'player')},
        ),
    ]
