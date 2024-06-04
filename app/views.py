from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, Http404, HttpResponseRedirect, HttpResponseRedirect
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import *
from app.forms import *
from app.decorators import *
from app.decorators import *
from json import dumps


# Create your views here.
@group_members_only
@group_members_only
@login_required(login_url="login")
def chat_view(req: HttpRequest, channel: str = "Cohort2") -> HttpResponse:
    context = {}
    try:
        chatroom = Group.objects.get(name=channel)
    except:
        return redirect("group_selection")  # Send home if bad group request
    
    if req.user in chatroom.banned_users.all():
        return redirect('group_selection')

    context["messages"] = chatroom.messages.all()
    form = SendMessage()
    users = [i.username for i in chatroom.users.all()]

    # Getting other user from private chat
    other_user = None
    if chatroom.is_private:
        if req.user not in chatroom.users.all():
            raise Http404()
        for user in chatroom.users.all():
            if user != req.user:
                other_user = user
                break

    if req.htmx:
        if req.method == "POST":
            form = SendMessage(req.POST)
            print(form)

    context["form"] = form
    context["current_user"] = req.user
    context["other_user"] = other_user
    context["channel"] = channel
    context["chatroom"] = chatroom
    return render(req, "ChatHome.html", context)


@login_required(login_url="login")
def profile_view(request: HttpRequest, username):
    context = {}

    try:
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        friend_request_from_current_user = FriendRequest.objects.filter(sender=request.user, receiver=user).exists()
        friend_request_from_other_user = FriendRequest.objects.filter(sender=user, receiver=request.user).exists()
    except:
        pass
        

    if request.method == 'POST':
        print(request.POST)
        if 'block_user' in request.POST:
            try:
                block = User.objects.get(pk=request.POST['user_id'])
                if block not in request.user.profile.blocked_users.all():
                    request.user.profile.blocked_users.add(block)
                if block in request.user.profile.friends.all():
                    request.user.profile.friends.remove(block)
            except:
                pass
        elif 'unblock_user' in request.POST:
            print('test')
            try:
                unblock = User.objects.get(pk=request.POST['user_id'])
                print('bi')
                if unblock in request.user.profile.blocked_users.all():
                    request.user.profile.blocked_users.remove(unblock)
                    print('gi')
            except:
                pass
    print(user.email)
    # context['user'] = UserProfile.objects.get(user = request.user)
    context["profile_info"] = user
    context["profile"] = profile
    context["friend_request_from_current_user"] = friend_request_from_current_user
    context["friend_request_from_other_user"] = friend_request_from_other_user

    return render(request, "profile.html", context)


def get_or_create_chatroom(request: HttpRequest, username):
    chatroom = None
    other_user = User.objects.get(username=username)
    my_private_chatrooms = request.user.chat_groups.filter(is_private=True)

    if my_private_chatrooms.exists():
        for cr in my_private_chatrooms:
            cr_users = cr.users.all()
            if other_user in cr_users:
                chatroom = cr
                break
            else:
                chatroom = Group.objects.create(is_private=True)
                chatroom.users.add(other_user, request.user)
    else:
        chatroom = Group.objects.create(is_private=True)
        chatroom.users.add(other_user, request.user)

    return chatroom


@login_required(login_url="login")
def chatroom_view(request: HttpRequest, username):

    chatroom = get_or_create_chatroom(request, username)
  
    return redirect("chatroom", chatroom.name)


@login_required(login_url="login")
def chat_file_upload(request: HttpRequest, channel):
    try:
        chatroom = Group.objects.get(name=channel)
    except:
        chatroom = None

    if request.htmx and request.FILES:
        file = request.FILES["file"]
        message = Message.objects.create(
            file=file,
            user=request.user,
            group=chatroom,
        )

        channel_layer = get_channel_layer()
        event = {
            "type": "message_handler",
            "message_id": message.id,
        }
        async_to_sync(channel_layer.group_send)(channel, event)
    return HttpResponse()


@unauthenticated_user
def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        if "just_signed_up" in request.session:
            del request.session["just_signed_up"]
            return redirect("profile-config")
        else:
            return redirect("group_selection")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("group_selection")
        else:
            messages.error(request, "Incorrect username and password combination")
    return render(request, "login.html")


@login_required(login_url="login")
def logout_view(request: HttpRequest):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def group_selection_view(request: HttpRequest):
    context = {}

    form = Create_Group_Form()

    try:
        groups = Group.objects.all()
        
    except:
        pass


    if request.method == "POST":
        form = Create_Group_Form(request.POST)
        if form.is_valid():
            new_group_chat = form.save(commit=False)
            new_group_chat.admin = request.user
            new_group_chat.save()
            new_group_chat.users.add(request.user)
            return redirect("chatroom", new_group_chat.name)

    context["form"] = form 
    context["groups"] = groups
    return render(request, "group_selection.html", {'groups':groups, 'form': form})

@unauthenticated_user
def registration_view(request: HttpRequest):
    if request.method == "POST":
        form = Create_User_Form(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session["just_signed_up"] = True
                return redirect("profile-config")
            else:
                messages.error(request, "Failed to log in. Please try again.")
        else:
            messages.info(request, form.errors)
    else:
        form = Create_User_Form()

    return render(request, "registration.html", {"form": form})

@login_required(login_url="login")
def make_profile_view(request):
    if UserProfile.objects.filter(user=request.user).exists():
        return redirect('group_selection')
    else:
        if request.method == "POST":
            form = Make_Profile_Form(request.POST, request.FILES)
            if form.is_valid():
                screen_name = form.cleaned_data["screen_name"]
                image = form.cleaned_data["image"]
                profile = create_user_profile(request.user, screen_name, image)
                return redirect("group_selection")
        else:
            form = Make_Profile_Form()

        return render(request, "make_profile.html", {"form": form})


@login_required(login_url="login")
def edit_profile_view(request: HttpRequest):
    user_profile = UserProfile.objects.get(user=request.user)
    user = User.objects.get(username=request.user)
    user_profile = UserProfile.objects.get(user = request.user)

    if request.method == "POST":
        new_screen_name = (
            user_profile.screen_name
            if not request.POST.get("screen_name")
            else request.POST.get("screen_name")
        )
        new_email = (
            user.email
            if not request.POST.get("new_email")
            else request.POST.get("new_email")
        )
        new_password = request.POST.get("password")
        new_image = request.FILES.get("image", user_profile.image)

        if "update" in request.POST:
            if new_password:
                update_password_result = update_password(user, new_password)
                if isinstance(update_password_result, str):
                    return render(
                        request,
                        "update_profile.html",
                        {"error": update_password_result},
                    )

            update_profile_info(user_profile, new_screen_name, new_image)
            update_user_email(user, new_email)

            return redirect("edit-profile")

        elif "delete" in request.POST:
            delete_user_profile(request.user)
            return redirect("login")

    return render(request, "update_profile.html", {"user": user_profile})


@login_required(login_url="login")
def create_group_view(request: HttpRequest):
    context = {}
    form = Create_Group_Form()

    if request.method == "POST":
        form = Create_Group_Form(request.POST)
        if form.is_valid():
            new_group_chat = form.save(commit=False)
            new_group_chat.admin = request.user
            new_group_chat.new_group_name = request.POST.get('new_group_name')
            new_group_chat.save()
            new_group_chat.users.add(request.user)
            return redirect("chatroom", new_group_chat.name)

    context["form"] = form
    return render(request, "create_group.html", context)

@admin_only_delete_group
@login_required(login_url="login")
def delete_group_view(request: HttpRequest, channel):
    try:
        chatroom = Group.objects.get(name=channel)
    except:
        chatroom = None

    chatroom.delete()
    return redirect("group_selection")


@login_required(login_url="login")
def delete_message_view(req: HttpRequest, channel: str, messageId: int):
    channel_layer = get_channel_layer()
    event = {
        "type": "delete_message",
        "message_id": f"{messageId}",
    }
    async_to_sync(channel_layer.group_send)(channel, event)
    return HttpResponse()


@login_required(login_url="login")
def update_message_view(req: HttpRequest):
    if req.method == "POST":
        channel_layer = get_channel_layer()
        event = {
            "type": "update_message",
            "message_id": req.POST.get("message_id"),
            "text": req.POST.get("text"),
        }
        async_to_sync(channel_layer.group_send)(req.POST.get("channel"), event)
        return HttpResponse()


@login_required(login_url="login")
def invite_user_list_view(request: HttpRequest, channel):
    context = {}

    try:
        chatroom = Group.objects.get(name=channel)
        my_profile = UserProfile.objects.get(user=request.user)
        friends = my_profile.friends.all()
    except:
        pass

    friend_invites = {}
    
    for friend in friends:
        current_user = User.objects.get(username=request.user)
        other_user = User.objects.get(username=friend)
        active_invite = InviteNotification.objects.filter(group=chatroom, sender=current_user, receiver=other_user).exists()
        friend_invites[friend] = active_invite

    context["chatroom"] = chatroom
    context["friend_invites"] = friend_invites
    return render(request, "user_invite.html", context)


@login_required(login_url="login")
def send_invite_view(request: HttpRequest, channel, username):
    try:
        chatroom = Group.objects.get(name=channel)
        user = User.objects.get(username=username)
    except:
        pass

    InviteNotification.objects.create(group=chatroom, sender=request.user, receiver=user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="login")
def cancel_invite_view(request: HttpRequest, channel, username):
    try:
        chatroom = Group.objects.get(name=channel)
        user = User.objects.get(username=username)
        invite = InviteNotification.objects.get(group=chatroom, sender=request.user, receiver=user)
    except:
        pass
    
    invite.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="login")
def accept_invite_view(request: HttpRequest, channel):
    try:
        chatroom = Group.objects.get(name=channel)
        invite = InviteNotification.objects.get(group=chatroom, receiver=request.user)
    except:
        pass

    chatroom.users.add(request.user)
    chatroom.save()
    invite.delete()

    return redirect("chatroom", chatroom.name)


@login_required(login_url="login")
def decline_invite_view(request: HttpRequest, channel):
    try:
        chatroom = Group.objects.get(name=channel)
        invite = InviteNotification.objects.get(group=chatroom, receiver=request.user)
    except:
        pass

    invite.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="login")
def invitations_view(request: HttpRequest):
    context = {}

    try:
        invitations = InviteNotification.objects.filter(receiver=request.user)
    except:
        pass

    context["invitations"] = invitations
    return render(request, "invitations.html", context)


@admin_or_moderators_group_management
@login_required(login_url="login")
def group_management_view(request: HttpRequest, channel):
    context = {}

    try:
        chatroom = Group.objects.get(name=channel)
        users = chatroom.users.exclude(username=request.user)
    except:
        chatroom = None
        users = None

    form = Create_Group_Form(instance=chatroom)

    if request.method == "POST":
        form = Create_Group_Form(request.POST, instance=chatroom)
        if form.is_valid():
            form.save()

    context["form"] = form
    context["chatroom"] = chatroom
    context["users"] = users
    context["current_user"] = request.user
    return render(request, "group_management.html", context)

@admin_only_moderator_manager
@login_required(login_url="login")
def appoint_moderators_view(request: HttpRequest, channel, username):
    try:
        chatroom = Group.objects.get(name=channel)
        user = User.objects.get(username=username)
    except:
        chatroom = None
        user = None

    chatroom.moderators.add(user)
    chatroom.save()
    return redirect("group_management", chatroom.name)


@admin_only_moderator_manager
@login_required(login_url="login")
def remove_moderators_view(request: HttpRequest, channel, username):
    try:
        chatroom = Group.objects.get(name=channel)
        user = User.objects.get(username=username)
    except:
        chatroom = None
        user = None

    chatroom.moderators.remove(user)
    chatroom.save()
    return redirect("group_management", chatroom.name)


@login_required(login_url="login")
def leave_group_view(request: HttpRequest, channel):
    try:
        chatroom = Group.objects.get(name=channel)
    except:
        pass

    if request.user in chatroom.moderators.all():
        chatroom.moderators.remove(request.user)
        chatroom.users.remove(request.user)
        chatroom.save()
    elif request.user != chatroom.admin and  request.user in chatroom.users.all():
        chatroom.users.remove(request.user)
        chatroom.save()

    return redirect("group_selection")


@login_required(login_url="login")
def send_friend_request_view(request: HttpRequest, username):
    try:
        sender = User.objects.get(username=request.user)
        receiver = User.objects.get(username=username)
    except:
        sender = None
        receiver = None

    FriendRequest.objects.create(sender=sender, receiver=receiver)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="login")
def remove_friend_review(request: HttpRequest, username):
    try:
        other_user = User.objects.get(username=username)
        current_user = User.objects.get(username=request.user) 
        other_user_friend_list = UserProfile.objects.get(user=other_user)
        current_user_friend_list = UserProfile.objects.get(user=current_user)
    except:
        other_user = None
        current_user = None
        other_user_friend_list = None
        current_user = None

    if other_user in current_user_friend_list.friends.all() and current_user in other_user_friend_list.friends.all():
        current_user_friend_list.friends.remove(other_user)
        other_user_friend_list.friends.remove(current_user)
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="login")
def accept_friend_request_view(request: HttpRequest, username):
    try:
        sender = User.objects.get(username=username)
        receiver = User.objects.get(username=request.user) 
        friend_request = FriendRequest.objects.get(sender=sender, receiver=receiver)
        sender_friends_list = UserProfile.objects.get(user=sender)
        receiver_friends_list=UserProfile.objects.get(user=receiver)
    except:
        sender = None
        receiver = None
        friend_request = None
        sender_friends_list = None
        receiver_friends_list = None

    if friend_request != None:
        receiver_friends_list.friends.add(sender)
        sender_friends_list.friends.add(receiver)
        friend_request.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="login")
def decline_friend_request_view(request: HttpRequest, username):
    try:
        sender = User.objects.get(username=username)
        receiver = User.objects.get(username=request.user) 
        friend_request = FriendRequest.objects.get(sender=sender, receiver=receiver)
    except:
        sender = None
        receiver = None
        friend_request = None

    if friend_request != None:
        friend_request.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="login")
def cancel_friend_request_view(request: HttpRequest, username):
    try:
        sender = User.objects.get(username=request.user)
        receiver = User.objects.get(username=username) 
        friend_request = FriendRequest.objects.get(sender=sender, receiver=receiver)
    except:
        sender = None
        receiver = None
        friend_request = None

    if friend_request != None:
        friend_request.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="login")
def friend_management_view(request: HttpRequest):
    return render(request, "friend_management.html")

def all_friends_view(request: HttpRequest):
    context = {}

    try:
        friend_list = UserProfile.objects.get(user=request.user)
    except:
        friend_list = None

    context["friend_list"] = friend_list
    return render(request, "all_friends.html", context)


@login_required(login_url="login")
def friend_requests_view(request: HttpRequest):
    context = {}

    try:
        friend_requests_list = FriendRequest.objects.filter(receiver=request.user)
    except:
        friend_requests_list = None

    context["friend_requests_list"] = friend_requests_list
    return render(request, "friend_requests.html", context)

def get_user_account(request: HttpRequest, userId: int, channel: str):
    try:
        user = User.objects.get(pk=f'{userId}')
        group = Group.objects.get(name=channel)
    except:
        user = None
        group = None

    return render(request, 'partials/account_popup_partial.html', {'found_user': user, 'group': group})

def ban_user(request: HttpRequest, userId: int, channel: str):
    if request.method == "POST":
        channel_layer = get_channel_layer()
        event = {
            "type": "ban_user",
            "user_id": userId
        }
        async_to_sync(channel_layer.group_send)(channel, event)
        return HttpResponse()

def unban_user(request: HttpRequest, userId: int, channel: str):
    if request.method == "POST":
        channel_layer = get_channel_layer()
        event = {
            "type": "unban_user",
            "user_id": userId
        }
        async_to_sync(channel_layer.group_send)(channel, event)
        return HttpResponse()
    
def search_users_view(request: HttpRequest):
    context = {}
    if request.method == "POST":
        search = request.POST['search']
        searched = User.objects.filter(username__contains=search)
    
        context["search"] = search
        context["searched"] = searched
    return render(request, "search_users.html", context)
    