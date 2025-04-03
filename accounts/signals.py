from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a user is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Save the user profile when the user is saved."""
    instance.profile.save()

@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def delete_user_profile(sender, instance, **kwargs):
    """Delete the user profile when the user is deleted."""
    try:
        instance.profile.delete()
    except UserProfile.DoesNotExist:
        pass 
