# Generated by Django 4.0.3 on 2022-04-09 20:27

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sets', models.PositiveIntegerField(choices=[(3, 'Three Set'), (5, 'Five Set')], default=3)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Player', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0, 'Love is the least expected minimum'), django.core.validators.MaxValueValidator(4, 'Score cannot exceed 5')])),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scoreboard.match')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scoreboard.player')),
            ],
        ),
        migrations.CreateModel(
            name='MatchStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_set', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Current set should be atleast 1'), django.core.validators.MaxValueValidator(5, 'Current set should not exceed 5')])),
                ('tiebreaker_active', models.BooleanField(default=False)),
                ('latest_event', models.CharField(blank=True, max_length=120, null=True)),
                ('match', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='scoreboard.match')),
                ('winner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='scoreboard.player')),
            ],
        ),
        migrations.AddField(
            model_name='match',
            name='players',
            field=models.ManyToManyField(to='scoreboard.player'),
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('set', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Set should be atleast 1'), django.core.validators.MaxValueValidator(5, 'Set should not exceed 5')])),
                ('games_won', models.PositiveIntegerField()),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scoreboard.match')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scoreboard.player')),
            ],
        ),
    ]
