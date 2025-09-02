from django.core.management.base import BaseCommand
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Reset weekly answer and question set counts'

    def handle(self, *args, **kwargs):
        UserProfile.objects.update(weekly_answer_count=0)
        self.stdout.write("Weekly limits reset.")
