from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Statistic
from mailing.models import AttemptMailing
from django.apps import AppConfig

@receiver(post_save, sender=AttemptMailing)
def update_user_stats(sender, instance, created, **kwargs):
    if created:
        statistic, created = Statistic.objects.get_or_create(user=instance.mailing.owner)
        if instance.status == 'success':
            statistic.successful_deliveries += 1
        elif instance.status == 'failure':
            statistic.unsuccessful_attempts += 1
        statistic.total_messages_sent += 1
        statistic.save()


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals