from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.timezone import now


class GenderChoices(models.TextChoices):
    MALE = 'M', _("Male")
    FEMALE = 'F', _("Female")
    OTHER = 'O', _("Other")
    UNDISCLOSED = 'U', _("Prefer not to say")


class CustomUser(AbstractUser):
    name = models.CharField(max_length=50, verbose_name=_("First Name"))
    surname = models.CharField(max_length=50, verbose_name=_("Last Name"))
    city = models.CharField(max_length=100, verbose_name=_("City"), blank=True, null=True)
    phone_number = models.CharField(max_length=20, verbose_name=_("Phone Number"), blank=True, null=True)
    gender = models.CharField(
        max_length=1,
        choices=GenderChoices.choices,
        default=GenderChoices.UNDISCLOSED,
        verbose_name=_("Gender"),
    )

    def __str__(self):
        return f"{self.username} ({self.name} {self.surname})"

    def get_full_name(self):
        full_name = f"{self.name} {self.surname}".strip()
        return full_name if full_name else self.username

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['username']


class PlanChoices(models.TextChoices):
    FREE = 'free', _('Free')
    PREMIUM = 'premium', _('Premium')


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    plan = models.CharField(max_length=10, choices=PlanChoices.choices, default=PlanChoices.FREE)
    weekly_answer_count = models.PositiveIntegerField(default=0)
    weekly_reset_date = models.DateField(default=timezone.now)
    next_reset = models.DateTimeField(default=lambda: now() + timedelta(days=7))

    def __str__(self):
        return f"{self.user.username} - {self.plan}"

    @property
    def max_weekly_answers(self):
        return 20 if self.plan == PlanChoices.PREMIUM else 5

    @property
    def remaining_answers(self):
        from diary.models import AnswerSession
        max_allowed = self.max_weekly_answers
        start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())
        used = AnswerSession.objects.filter(
            respondent=self.user,
            created_at__date__gte=start_of_week
        ).count()
        return max(max_allowed - used, 0)

    def reset_weekly_answers(self):
        now_dt = timezone.now()
        if now_dt >= self.next_reset:
            self.weekly_answer_count = 0
            self.weekly_reset_date = now_dt.date()
            self.next_reset = now_dt + timedelta(days=7)
            self.save()


class NotificationType(models.TextChoices):
    ANSWERED_DIARY = "answered_diary", _("Answered Diary")
    RECEIVED_RESPONSE = "received_response", _("Received Response")
    SYSTEM = "system", _("System")


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("User"),
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
        verbose_name=_("Actor"),
    )
    type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        verbose_name=_("Type"),
    )
    related_object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Related Object ID"))
    message = models.CharField(max_length=255, verbose_name=_("Message"))

    answer_session = models.ForeignKey(
        'diary.AnswerSession',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name=_("Answer Session"),
    )
    question_set = models.ForeignKey(
        'diary.QuestionSet',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name=_("Question Set"),
    )

    is_read = models.BooleanField(default=False, verbose_name=_("Is Read"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=["is_read"])

    def get_link(self):
        if self.related_object_id and self.type in (
            NotificationType.ANSWERED_DIARY,
            NotificationType.RECEIVED_RESPONSE,
        ):
            return reverse("diary:view_single_response", kwargs={"session_id": self.related_object_id})
        return None
