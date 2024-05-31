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