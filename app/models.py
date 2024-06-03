from django.db import models
from django.contrib.auth.models import User
import shortuuid, os


# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=200, default=shortuuid.uuid)
    new_group_name = models.CharField(max_length=200, null=True, blank=True)
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="group_chats",
        null=True,
        blank=True,
    )
    moderators = models.ManyToManyField(User, blank=True)
    users = models.ManyToManyField(User, related_name="chat_groups", blank=True)
    is_private = models.BooleanField(default=False)
    users_online = models.ManyToManyField(User, related_name = 'online', blank = True)
    banned_users = models.ManyToManyField(User, related_name='banned_from', blank=True)

    def __str__(self):
        if self.new_group_name:
            return self.new_group_name
        elif self.is_private == True:
            return f"Private chat: {self.name}"
        else:
            return self.name


class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField()
    file = models.FileField(upload_to="files/", blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_invitation = models.BooleanField(default=False)

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None

    def __str__(self):
        if self.text:
            return f'"{self.text[:10] + "..." if len(self.text) > 10 else self.text}" by {self.user.username} in {self.group.name}'
        elif self.file:
            return f'"{self.filename}" by {self.user.username} in {self.group.name}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    screen_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="", null=True, blank=True)
    friends = models.ManyToManyField(User, related_name="friends", blank=True )
    blocked_users = models.ManyToManyField(User, related_name='blocked_by', blank=True)

    def __str__(self):
        return f"@{self.user.username}"
    
class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")

    def __str__(self):
        return f"{self.sender} to {self.receiver}"


############################################Create########################
def create_user_profile(user, screen_name, image):
    return UserProfile.objects.create(user=user, screen_name=screen_name, image=image)


# ====={ update }===== #
def update_profile_info(user, screen_name, image=None):
    user.screen_name = screen_name
    user.image = image
    user.save()


def update_user_email(user, email):
    user.email = email
    user.save()


def update_password(user, password):
    if user.check_password(password):
        return "New password cannot be the same as the old password."
    user.set_password(password)
    user.save()


# ====={ delete }===== #
def delete_user_profile(user):
    User.objects.get(username=user).delete()
