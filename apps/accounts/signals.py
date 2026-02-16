# Create UserProfile with default role when User is created (LDAP or local)
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Role, UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        default_role = Role.objects.filter(name=Role.RoleName.VIEWER).first()
        UserProfile.objects.get_or_create(user=instance, defaults={"role": default_role})
