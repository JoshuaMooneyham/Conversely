from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # return f"{self.user.username}: {self.text}" # <-- changed to test longer messages
        return f'"{self.text[:10] + "..." if len(self.text) > 10 else self.text}" by {self.user.username} in {self.group.name}'
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    screen_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='', null=True, blank=True)

    def __str__(self):
        return f'@{self.user.username}'