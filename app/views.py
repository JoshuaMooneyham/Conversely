from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, Http404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import *
from app.forms import *


# Create your views here.
def chat_view(req: HttpRequest, channel: str = "Cohort2") -> HttpResponse:
    context = {}
    try:
        chatroom = Group.objects.get(name=channel)
    except:
        pass
        # return redirect('home') # Send home if bad group request
    context["messages"] = chatroom.messages.all()
    form = SendMessage()

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
        form = SendMessage(req.POST)
        if form.is_valid():
            newMessage = form.save(commit=False)
            newMessage.user = req.user
            newMessage.group = chatroom
            form.save()
            form = SendMessage()
            return render(
                req, "message_partial.html", {"message": newMessage, "user": req.user}
            )

    context["form"] = form
    context["other_user"] = other_user
    context["channel"] = channel
    context["chatroom"] = chatroom
    return render(req, "ChatHome.html", context)


def profile_view(request: HttpRequest, username):
    context = {}
    current_user = request.user

    try:
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        admin_groups = current_user.group_chats.all()
    except:
        user = None
        profile = None
        admin_groups = None

    context["current_user"] = current_user
    context["profile"] = profile
    context["admin_groups"] = admin_groups
    return render(request, "profile.html", context)


def get_or_create_chatroom(request: HttpRequest, username):
    if request.user.username == username:
        return redirect("chat_home")

    other_user = User.objects.get(username=username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)

    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.users.all():
                chatroom = chatroom
                break
            else:
                chatroom = Group.objects.create(is_private=True)
                chatroom.users.add(other_user, request.user)
    else:
        chatroom = Group.objects.create(is_private=True)
        chatroom.users.add(other_user, request.user)

    return redirect("chatroom", chatroom.name)


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
    return HttpResponse


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


def logout_view(request: HttpRequest):
    logout(request)
    return redirect("login")


def group_selection_view(request: HttpRequest):
    return render(request, "group_selection.html")


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


def make_profile_view(request: HttpRequest):
    if request.method == "POST":
        form = Make_Profile_Form(request.POST)
        if form.is_valid():
            screen_name = form.cleaned_data["screen_name"]
            image = form.cleaned_data["image"]
            create_user_profile(request.user, screen_name, image)
            return redirect("group_selection")
    else:
        form = Make_Profile_Form()

    return render(request, "make_profile.html", {"form": form})


def create_group_view(request: HttpRequest):
    context = {}
    form = Create_Group_Form()

    if request.method == "POST":
        form = Create_Group_Form(request.POST)
        if form.is_valid():
            new_group_chat = form.save(commit=False)
            new_group_chat.admin = request.user
            new_group_chat.save()
            new_group_chat.users.add(request.user)
            return redirect("chatroom", new_group_chat.name)

    context["form"] = form
    return render(request, "create_group.html", context)


def update_group_view(request: HttpRequest, group_name):
    context = {}

    try:
        selected_group = Group.objects.get(
            admin=request.user, new_group_name=group_name
        )
    except:
        selected_group = None

    form = Create_Group_Form(instance=selected_group)

    if request.method == "POST":
        form = Create_Group_Form(request.POST, instance=selected_group)
        if form.is_valid():
            form.save()
            return redirect(f"/profile/{request.user}")

    context["form"] = form
    return render(request, "create_group.html", context)


def delete_group_view(request: HttpRequest, group_name):
    try:
        selected_group = Group.objects.get(
            admin=request.user, new_group_name=group_name
        )
    except:
        selected_group = None

    selected_group.delete()
    return redirect(f"/profile/{request.user}")
