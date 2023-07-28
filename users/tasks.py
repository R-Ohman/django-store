from celery import shared_task
from django.utils import timezone

from email_app.models import EmailManager
from users.models import User


@shared_task(bind=True)
def invite_users_to_visit(self):
    users = User.objects.filter(is_active=True, is_confirmed=True)
    for user in users:
        if timezone.now() - user.last_login > timezone.timedelta(days=3):
            EmailManager.invite_and_recommendation(user)
    return 'Done'
