from django.http import HttpResponse
from django.shortcuts import redirect
from app.models import Group, User

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("group_selection")
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func

def group_members_only(view_func):
    def wrapper_func(request, channel, *args, **kwargs):
        chatroom = Group.objects.get(name=channel)
        if chatroom.new_group_name or chatroom.is_private:
            if request.user not in chatroom.users.all():
                return HttpResponse("You are not a member of this group.")
        return view_func(request, channel, *args, **kwargs)
    return wrapper_func

def admin_or_moderators_group_management(view_func):
    def wrapper_func(request, channel, *args, **kwargs):
        chatroom = Group.objects.get(name=channel)
        if request.user != chatroom.admin and request.user not in chatroom.moderators.all():
            return HttpResponse("Must be the admin or a moderator of this group.")
        return view_func(request, channel, *args, **kwargs)
    return wrapper_func

def admin_or_moderators_update_group(view_func):
    def wrapper_func(request, channel, *args, **kwargs):
        chatroom = Group.objects.get(name=channel)
        if request.user != chatroom.admin and request.user not in chatroom.moderators.all():
            return HttpResponse("Must be the admin or a moderator of this group.")
        return view_func(request, channel, *args, **kwargs)
    return wrapper_func

def admin_only_delete_group(view_func):
    def wrapper_func(request, channel, *args, **kwargs):
        chatroom = Group.objects.get(name=channel)
        if request.user != chatroom.admin:
            return HttpResponse("Must be the admin of this group.")
        return view_func(request, channel, *args, **kwargs)
    return wrapper_func

def admin_only_moderator_manager(view_func):
    def wrapper_func(request, channel, username, *args, **kwargs):
        chatroom = Group.objects.get(name=channel)
        if request.user != chatroom.admin:
            return HttpResponse("Must be the admin of this group.")
        return view_func(request, channel, username, *args, **kwargs)
    return wrapper_func
        