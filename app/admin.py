from django.contrib import admin
from app.models import *

# Register your models here.
admin.site.register(Group)
admin.site.register(Message)
admin.site.register(UserProfile)