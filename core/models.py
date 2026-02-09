from django.db import models
from django.utils import timezone


class Cadet(models.Model):
    level = models.FloatField(default=1.0)
    hp_current = models.PositiveIntegerField(default=1020)
    xp_total = models.PositiveIntegerField(default=0)
    wallet = models.PositiveIntegerField(default=0)
    avatar_state = models.CharField(max_length=50, default="Neutral")
    stat_str = models.PositiveSmallIntegerField(default=0)
    stat_int = models.PositiveSmallIntegerField(default=0)
    stat_wis = models.PositiveSmallIntegerField(default=0)
    stat_vit = models.PositiveSmallIntegerField(default=0)
    blackhole_date = models.DateField(default=timezone.now)

    def __str__(self) -> str:
        return f"Cadet Lv {self.level:.2f}"


class Resource(models.Model):
    class ResourceType(models.TextChoices):
        YOUTUBE = "youtube", "YouTube"
        PDF = "pdf", "PDF"
        BOOK = "book", "Book"

    title = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices)
    url = models.URLField()
    tier = models.CharField(max_length=1, default="B", help_text="S/A/B tier rating")

    def __str__(self) -> str:
        return f"{self.title} ({self.resource_type})"


class Project(models.Model):
    class ProjectType(models.TextChoices):
        CODE = "code", "Code"
        LIFE = "life", "Life"
        EXAM = "exam", "Exam"

    name = models.CharField(max_length=255)
    project_type = models.CharField(max_length=10, choices=ProjectType.choices)
    coordinates_x = models.IntegerField()
    coordinates_y = models.IntegerField()
    dependencies = models.ManyToManyField("self", blank=True, symmetrical=False)
    resource = models.ForeignKey(Resource, null=True, blank=True, on_delete=models.SET_NULL)
    min_stat_str = models.PositiveSmallIntegerField(default=0)
    min_stat_int = models.PositiveSmallIntegerField(default=0)
    min_stat_wis = models.PositiveSmallIntegerField(default=0)
    min_stat_vit = models.PositiveSmallIntegerField(default=0)

    def meets_stat_requirements(self, cadet: Cadet) -> bool:
        return all(
            [
                cadet.stat_str >= self.min_stat_str,
                cadet.stat_int >= self.min_stat_int,
                cadet.stat_wis >= self.min_stat_wis,
                cadet.stat_vit >= self.min_stat_vit,
            ]
        )

    def can_unlock(self, cadet: Cadet, completed_project_ids: set[int]) -> bool:
        if not self.meets_stat_requirements(cadet):
            return False
        dependency_ids = set(self.dependencies.values_list("id", flat=True))
        return dependency_ids.issubset(completed_project_ids)

    def __str__(self) -> str:
        return self.name


class LifeLog(models.Model):
    class ActivityType(models.TextChoices):
        CODE = "code", "Code"
        SLEEP = "sleep", "Sleep"
        EAT = "eat", "Eat"
        SPORT = "sport", "Sport"
        LISTEN_ENGLISH = "listen_english", "Listen English"
        BREATH = "breath", "Breath"

    class Grade(models.TextChoices):
        S = "S", "S"
        A = "A", "A"
        B = "B", "B"
        F = "F", "F"

    cadet = models.ForeignKey(Cadet, on_delete=models.CASCADE, related_name="life_logs")
    activity_type = models.CharField(max_length=30, choices=ActivityType.choices)
    duration = models.DurationField()
    admin_grade = models.CharField(max_length=1, choices=Grade.choices)
    xp_gained = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_xp(self) -> int:
        grade_multiplier = {
            self.Grade.S: 1.5,
            self.Grade.A: 1.2,
            self.Grade.B: 1.0,
            self.Grade.F: 0.2,
        }
        minutes = int(self.duration.total_seconds() // 60)
        return int(minutes * grade_multiplier[self.admin_grade])

    def apply_stat_rewards(self) -> None:
        minutes = int(self.duration.total_seconds() // 60)
        base_points = max(1, minutes // 30)
        if self.activity_type in {self.ActivityType.CODE, self.ActivityType.SPORT}:
            self.cadet.stat_str += base_points if self.activity_type == self.ActivityType.SPORT else 0
            self.cadet.stat_int += base_points if self.activity_type == self.ActivityType.CODE else 0
        elif self.activity_type in {self.ActivityType.SLEEP, self.ActivityType.BREATH}:
            self.cadet.stat_vit += base_points
        elif self.activity_type in {self.ActivityType.EAT}:
            self.cadet.stat_str += base_points
        elif self.activity_type == self.ActivityType.LISTEN_ENGLISH:
            self.cadet.stat_wis += base_points
        self.cadet.save(update_fields=["stat_str", "stat_int", "stat_wis", "stat_vit"])

    def save(self, *args, **kwargs) -> None:
        self.xp_gained = self.calculate_xp()
        super().save(*args, **kwargs)
        self.apply_stat_rewards()

    def __str__(self) -> str:
        return f"{self.get_activity_type_display()} ({self.duration})"
