from django.conf import settings
from django.db import models
from django.utils import timezone


def default_stats() -> dict[str, int]:
    return {"STR": 0, "INT": 0, "WIS": 0}


class Cadet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    hp_daily = models.PositiveIntegerField(default=0)
    blackhole_date = models.DateField(default=timezone.now)
    stats = models.JSONField(default=default_stats)

    def __str__(self) -> str:
        return f"{self.user} (Lv {self.level})"


class Project(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    xp_reward = models.PositiveIntegerField()
    estimated_time = models.DurationField(help_text="Estimated time to complete")
    graph_x = models.IntegerField()
    graph_y = models.IntegerField()
    dependencies = models.ManyToManyField("self", blank=True, symmetrical=False)

    def __str__(self) -> str:
        return self.name


class LifeLog(models.Model):
    class Activity(models.TextChoices):
        CODE = "code", "Code"
        SLEEP = "sleep", "Sleep"
        SPORT = "sport", "Sport"

    class Grade(models.TextChoices):
        S = "S", "S"
        A = "A", "A"
        B = "B", "B"
        F = "F", "F"

    activity = models.CharField(max_length=20, choices=Activity.choices)
    duration = models.DurationField()
    admin_grade = models.CharField(max_length=1, choices=Grade.choices)
    is_verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.get_activity_display()} ({self.duration})"
