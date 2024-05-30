from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from app.models import *

class SendMessage(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']

class Create_User_Form(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class Make_Profile_Form(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['screen_name', 'image']


    # this was supposed to assign the default image from the static folder but isn't working
    # def set_profile_pic(self):
    #     image = self.cleaned_data.get('image')
    #     if not image:
    #         self.cleaned_data['image'] = 'images/default-user.jpg'
    #     return image