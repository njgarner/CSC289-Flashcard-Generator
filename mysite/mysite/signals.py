from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:  # only create the profile when a new user is created
        if not hasattr(instance, 'userprofile'):  # check if the user already has a profile
            UserProfile.objects.create(user=instance, role='student')  # Default to student
    else:
        # Ensure the profile is updated if the user is updated
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
