
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from django_extensions.db.models import TimeStampedModel


# =============================================================================
# USER PROFILE
# =============================================================================

class UserProfile(models.Model):
    # This model is automatically create when a user is created
    # check ingest.signals.py

    user = models.OneToOneField(
        User, related_name="profile",
        on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return str(self.user)


# =============================================================================
# RAW FILE UPLOAD
# =============================================================================

def _raw_file_upload_to(instance, filename):
    full_name = f"raw_{instance.id}_{filename}"
    import ipdb; ipdb.set_trace()
    return '/'.join([settings.ATTACHMENTS, "raw_files", folder, full_name])


class RawFile(TimeStampedModel):

    file = models.FileField(upload_to=_raw_file_upload_to)
    confirmed = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        User, related_name="raw_files",
        on_delete=models.CASCADE, verbose_name="Created by")

    @property
    def filename(self):
        return self.file.url.rsplit("/", 1)[-1]

    @property
    def filext(self):
        return os.path.splitext(self.filename)