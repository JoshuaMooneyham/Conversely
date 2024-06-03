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
    
    # User Management
    path("make-profile", make_profile_view, name="profile-config"),
    path("profile/<str:username>/", profile_view, name="profile"),
    path("update-profile", edit_profile_view, name="edit-profile"),

    # Group Management
    path("<str:channel>/manage", group_management_view, name="group_management"),
    path("update/<str:channel>/", update_group_view, name="update_group"),
    path("delete/<str:channel>/", delete_group_view, name="delete_group"),
    path("make-moderator/<str:channel>/<str:username>/", appoint_moderators_view, name="appoint_moderators"),
    path("remove-moderator/<str:channel>/<str:username>/", remove_moderators_view, name="remove_moderators"),
    path("<str:channel>/invite-users/", invite_user_list_view, name="invite_users"),
    path("send-invite/<str:channel>/<str:username>/", send_invite_view, name="send_invite"),
    path("cancel-invite/<str:channel>/<str:username>/", cancel_invite_view, name="cancel_invite"),
    path("accept-invite/<str:channel>/", accept_invite_view, name="accept_invite"),
    path("decline-invite/<str:channel>/", decline_invite_view, name="decline_invite"),
    path("invitations", invitations_view, name="invitations"),
    path("leave/<str:channel>/", leave_group_view, name="leave_chatroom"),

    # Message Management
    path("messages/delete/<str:channel>/<int:messageId>/", delete_message_view, name="delete_message"),
    path("messages/update/", update_message_view, name="update_message"),
    path("chat/fileupload/<str:channel>/", chat_file_upload, name="chat-file-upload"),

    #Friend Management
    path("friend-management", friend_management_view, name="friend_management"),
    path("friend-list", all_friends_view, name="friend_list"),
    path("friend-requests", friend_requests_view, name="friend_requests"),
    path("<str:username>/add-friend", send_friend_request_view, name="add_friend"),
    path("<str:username>/remove-friend", remove_friend_review, name="remove_friend"),
    path("<str:username>/accept-friend", accept_friend_request_view, name="accept_friend"),
    path("<str:username>/decline-friend", decline_friend_request_view, name="decline_friend"),
    path("<str:username>/cancel-request", cancel_friend_request_view, name="cancel_request"),
    path("search/", search_users_view, name="search_users"), 

    # User Navigation
    path("group-selection/", group_selection_view, name="group_selection"),

    # ==={ Private Rooms }=== #
    path("chat/<str:username>/", chatroom_view, name="private_chat"),
    path("chat/room/<str:channel>/", chat_view, name="chatroom"),
    
    # ==={ User Account Popup}=== #
    path("popup/<int:userId>/<str:channel>/", get_user_account, name="get_user_account"),
    path("ban/<int:userId>/<str:channel>/", ban_user, name="ban_user"),
    path("unban/<int:userId>/<str:channel>/", unban_user, name="unban_user"),

    # ==={ File Serving }=== #
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
]
