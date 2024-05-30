from django.db import models
from django.contrib.auth.models import User
import shortuuid, os


# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=200, default=shortuuid.uuid)
    users = models.ManyToManyField(User, related_name="chat_groups", blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField()
    file = models.FileField(upload_to="files/", blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None

    def __str__(self):
        # return f"{self.user.username}: {self.text}" # <-- changed to test longer messages
        if self.text:
            return f'"{self.text[:10] + "..." if len(self.text) > 10 else self.text}" by {self.user.username} in {self.group.name}'
        elif self.file:
            return f'"{self.filename}" by {self.user.username} in {self.group.name}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    screen_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="", null=True, blank=True)

    def __str__(self):
        return f"@{self.user.username}"
