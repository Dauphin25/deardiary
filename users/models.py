import datetime
import profile
from datetime import timedelta

from django.contrib.auth.models import AbstractUser  # Base user model with built-in auth features
from django.db import models  # Django ORM for defining database fields
from django.utils.translation import gettext_lazy as _  # For making text translatable
from diary.models import AnswerSession, QuestionSet  # ✅ use the real models
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now



# Gender choices outside the model
class GenderChoices(models.TextChoices):
    MALE = 'M', _("Male")
    FEMALE = 'F', _("Female")
    OTHER = 'O', _("Other")
    UNDISCLOSED = 'U', _("Prefer not to say")


# Custom user model that extends Django's AbstractUser
class CustomUser(AbstractUser):
    # Full name fields
    name = models.CharField(
        max_length=50,
        verbose_name=_("First Name"),
        help_text=_("Enter your first name."),
    )
    surname = models.CharField(
        max_length=50,
        verbose_name=_("Last Name"),
        help_text=_("Enter your last name."),
    )

    # Optional location fields
    city = models.CharField(
        max_length=100,
        verbose_name=_("City"),
        help_text=_("Where do you live?"),
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name=_("Phone Number"),
        help_text=_("Optional phone number for contact."),
        blank=True,
        null=True,
    )

    # Use GenderChoices defined above
    gender = models.CharField(
        max_length=1,
        choices=GenderChoices.choices,
        default=GenderChoices.UNDISCLOSED,
        verbose_name=_("Gender"),
        help_text=_("Select your gender."),
    )

    # Override string representation
    def __str__(self):
        return f"{self.username} ({self.name} {self.surname})"


    def get_full_name(self):
        """
        Return the user's full name in "First Last" format.
        If both fields are empty, fallback to username.
        """
        full_name = f"{self.name} {self.surname}".strip()
        return full_name if full_name else self.username



    # Define metadata for admin panel and queryset
    class Meta:
        verbose_name = _("User")  # Singular name in admin
        verbose_name_plural = _("Users")  # Plural name in admin
        ordering = ['username']  # Default ordering by username

class PlanChoices(models.TextChoices):
    FREE = 'free', _('Free')
    PREMIUM = 'premium', _('Premium')

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    plan = models.CharField(
        max_length=10,
        choices=PlanChoices.choices,
        default=PlanChoices.FREE
    )
    weekly_answer_count = models.PositiveIntegerField(default=0)
    weekly_reset_date = models.DateField(default=timezone.now)  # track last reset
    next_reset = models.DateTimeField(default=lambda: now() + timedelta(days=7))  # ✅ 7 days later

    def __str__(self):
        return f"{self.user.username} - {self.plan}"

    @property
    def max_weekly_answers(self):
        """Return max answers per week depending on plan."""
        return 20 if self.plan == PlanChoices.PREMIUM else 5

    @property
    def remaining_answers(self):
        """Return remaining answers for this week."""
        # figure out max per user type
        max_allowed = self.max_weekly_answers

        # define start of current week (Monday as start, adjust if needed)
        start_of_week = timezone.now().date() - timedelta(days=timezone.now().weekday())

        # count AnswerSessions directly (not diaries)
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
    ANSWERED_DIARY = "answered_diary", _("Answered Diary")   # someone answered your diary
    RECEIVED_RESPONSE = "received_response", _("Received Response")  # you answered someone’s diary
    SYSTEM = "system", _("System")  # for future use


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
        help_text=_("The user who triggered this notification."),
    )
    type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        verbose_name=_("Type"),
    )
    related_object_id = models.UUIDField(null=True, blank=True, verbose_name=_("Related Object ID"))
    message = models.CharField(max_length=255, verbose_name=_("Message"))

    # ✅ Link to actual objects
    answer_session = models.ForeignKey(
        AnswerSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name=_("Answer Session"),
    )
    question_set = models.ForeignKey(
        QuestionSet,
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
        if self.type == NotificationType.ANSWERED_DIARY:
            return reverse("diary:response_session_detail", kwargs={"pk": self.related_object_id})
        elif self.type == NotificationType.RECEIVED_RESPONSE:
            return reverse("diary:response_session_detail", kwargs={"pk": self.related_object_id})
        return None
