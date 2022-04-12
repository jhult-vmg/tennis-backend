# Generated by Django 4.0.3 on 2022-04-12 22:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scoreboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchstatus',
            name='latest_event',
            field=models.CharField(blank=True, default='Match Started', max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='point',
            name='score',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0, 'Love is the least expected minimum'), django.core.validators.MaxValueValidator(4, 'Score cannot exceed 4')]),
        ),
    ]