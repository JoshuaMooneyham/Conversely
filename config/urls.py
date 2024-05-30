"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from config import settings
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from app.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('auth/login/', LoginView.as_view, name='login')
    path("<str:channel>/", chat_view, name="chat_home"),
    path("profile/<str:username>/", profile_view, name="profile"),
    path("chat/<str:username>/", get_or_create_chatroom, name="private_chat"),
    path("chat/private/<str:channel>/", chat_view, name="chatroom"),
    path("chat/fileupload/<str:channel>", chat_file_upload, name="chat-file-upload"),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
]
