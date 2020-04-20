
from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User

from django.dispatch import receiver

from django_extensions.db.models import TimeStampedModel


# =============================================================================
# USER PROFILE
# =============================================================================

class UserProfile(TimeStampedModel):

    user = models.OneToOneField(
        User, related_name="profile",
        on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()

