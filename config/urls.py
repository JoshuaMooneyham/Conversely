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
    # User Authentication
    path("", login_view, name="login"),
    path("registration/", registration_view, name="registration"),
    path("logout/", logout_view, name="logout"),
    path("admin/", admin.site.urls),
    # path('auth/login/', LoginView.as_view, name='login')
    path("", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("group-selection/", group_selection_view, name="group_selection"),
    path("registration", registration_view, name="registration"),
    path("make-profile", make_profile_view, name="profile-config"),
    path("update-profile", edit_profile_view, name="edit-profile"),
    path("<str:channel>/", chat_view, name="chat_home"),
    # User Management
    path("make-profile", make_profile_view, name="profile-config"),
    path("profile/<str:username>/", profile_view, name="profile"),
    path("update-profile", edit_profile_view, name="edit-profile"),
    # Group Management
    path("update/<str:group_name>/", update_group_view, name="update_group"),
    path("delete/<str:group_name>/", delete_group_view, name="delete_group"),
    path("create", create_group_view, name="create_group"),
    # Message Management
    path(
        "messages/delete/<str:channel>/<int:messageId>/",
        delete_message_view,
        name="delete_message",
    ),
    path("messages/update/", update_message_view, name="update_message"),
    path("chat/fileupload/<str:channel>/", chat_file_upload, name="chat-file-upload"),
    # User Navigation
    path("group-selection/", group_selection_view, name="group_selection"),
    path("<str:channel>/", chat_view, name="chat_home"),
    path("chat/group/<str:channel>/", chat_view, name="group_chatroom"),
    # Private Rooms
    path("chat/<str:username>/", get_or_create_chatroom, name="private_chat"),
    path("chat/room/<str:channel>/", chat_view, name="chatroom"),
    path("chat/fileupload/<str:channel>", chat_file_upload, name="chat-file-upload"),
    path("create", create_group_view, name="create_group"),
    path("update/<str:group_name>/", update_group_view, name="update_group"),
    path("delete/<str:group_name>/", delete_group_view, name="delete_group"),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
]
