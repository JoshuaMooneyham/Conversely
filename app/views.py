from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, Http404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
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
    return render(req, "ChatHome.html", context)


def profile_view(request, username):
    context = {}
    current_user = request.user

    try:
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
    except:
        user = None
        profile = None

    context["current_user"] = current_user
    context["profile"] = profile
    return render(request, "profile.html", context)


def get_or_create_chatroom(request, username):
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


def chat_file_upload(request, channel):
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
