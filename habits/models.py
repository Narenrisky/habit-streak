from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

# Create your models here.
class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_habit_per_user'
            )
        ]

    def __str__(self):
        return self.name

    def get_current_streak(self):
        today = timezone.now().date()
        streak = 0

        logs = self.habitlog_set.values_list('date', flat=True)
        expected_day = today

        for log_date in logs:
            if log_date == expected_day:
                streak += 1
                expected_day -= timedelta(days=1)
            else:
                break
        return streak

    def is_done_on(self, date):
        return self.habitlog_set.filter(date=date).exists()

    def total_completions(self):
        return self.habitlog_set.count()

    def longest_streak(self):
        logs = list(
            self.habitlog_set
            .order_by('date')
            .values_list('date', flat=True)
        )

        longest = 0
        current = 0
        prev_date = None

        for date in logs:
            if prev_date and date == prev_date + timedelta(days=1):
                current += 1
            else:
                current = 1
            longest = max(longest, current)
            prev_date = date
        return longest

    def weekly_consistency_percentage(self):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())

        completed_days = self.habitlog_set.filter(
            date__gte=start_of_week,
            date__lte=today
        ).count()

        days_so_far = today.weekday() + 1
        return round((completed_days / days_so_far) * 100, 1)

class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('habit', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.habit.name} - {self.date}"