from django import forms
from app.models import *

class SendMessage(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
