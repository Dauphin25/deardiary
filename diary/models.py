from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils.text import slugify
from unidecode import unidecode


class QuestionSetStyle(models.Model):
    """
    Defines visual or layout style for a QuestionSet (e.g., color, font, theme).
    """
    name = models.CharField(_("Style Name"), max_length=50, unique=True)
    description = models.TextField(_("Description"), blank=True)
    template_name = models.CharField(_("Template Filename"), max_length=100, help_text=_("e.g. 'style_grunge.html'"))
    created_at = models.DateTimeField(auto_now_add=True)
    is_premium = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Question Set Style")
        verbose_name_plural = _("Question Set Styles")
        ordering = ['name']

    def __str__(self):
        return self.name

class QuestionSet(models.Model):
    """A set of custom questions created by a user."""

    style = models.ForeignKey(
        QuestionSetStyle,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Style"),
        related_name="question_sets"
    )


    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="question_sets",
        verbose_name=_("Owner"),
        help_text=_("User who created this question set.")
    )

    # ✅ Add a UUID just for sharing
    # ✅ Generate a unique UUID automatically for sharing
    share_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        help_text=_("Title of the question set.")
    )

    slug = models.SlugField(max_length=255, unique=True, blank=True)

    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Optional description for this question set.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )

    class Meta:
        verbose_name = _("Question Set")
        verbose_name_plural = _("Question Sets")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.owner.username})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while QuestionSet.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slugify(unidecode(self.title))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("diary:question_set_detail", kwargs={"slug": self.slug})

class Question(models.Model):
    """A single question within a question set."""
    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("Question Set")
    )
    text = models.TextField(
        verbose_name=_("Question Text"),
        help_text=_("The text of the question.")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_("Order of the question in the set.")
    )

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ["order"]

    def __str__(self):
        return f"Q{self.order + 1}: {self.text[:50]}"


class AnswerSession(models.Model):
    """A session where a friend answers a full question set."""
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="answer_sessions",
        verbose_name=_("Respondent"),
        help_text=_("The user who answered these questions.")
    )
    question_set = models.ForeignKey(
        QuestionSet,
        on_delete=models.SET_NULL,
        null=True,  # allow database NULL when the diary is deleted
        blank=True,  # allow empty in forms/admin
        related_name="answer_sessions",
        verbose_name=_("Question Set")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Answered At")
    )

    class Meta:
        verbose_name = _("Answer Session")
        verbose_name_plural = _("Answer Sessions")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Session by {self.respondent or 'Anonymous'} on {self.created_at.strftime('%Y-%m-%d')}"

class Answer(models.Model):
    """An individual answer to a question, part of a session."""
    session = models.ForeignKey(
        "AnswerSession",  # keep as string if defined later in file
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("Answer Session")
    )
    question = models.ForeignKey(
        "Question",  # keep relation so you can still link back
        on_delete=models.SET_NULL,  # if question deleted, keep snapshot
        null=True,
        blank=True,
        related_name="answers",
        verbose_name=_("Question")
    )
    # Snapshot field: keeps original question text at the time of answering
    question_text = models.TextField(
        verbose_name=_("Original Question Text"),
        help_text=_("Stores the question text at the time of answering."),
        default=""
    )
    text = models.TextField(
        verbose_name=_("Answer Text"),
        help_text=_("Text provided as an answer to the question.")
    )

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
        unique_together = ("session", "question")

    def save(self, *args, **kwargs):
        """
        On save, if no snapshot exists yet, copy the current question text.
        """
        if self.question and not self.question_text:
            self.question_text = self.question.text
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer to '{self.question_text[:30]}': {self.text[:30]}"


class NewsItem(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name=_("Title"),
        help_text=_("Short headline for the news item.")
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("A brief description or details about the news.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("Lower numbers appear first. For example, 1 = first position.")
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Created At")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Uncheck to hide this news item from the homepage.")
    )

    class Meta:
        verbose_name = _("News Item")
        verbose_name_plural = _("News Items")
        ordering = ['display_order', '-created_at']  # manual order first, newest after

    def __str__(self):
        return f"{self.display_order} - {self.title}"