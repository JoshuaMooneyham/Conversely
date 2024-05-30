from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, Http404
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

    # if req.method == 'POST':
    #     form = SendMessage(req.POST)
    #     if form.is_valid():
    #         newMessage = form.save(commit=False)
    #         newMessage.user = req.user
    #         newMessage.group = chatroom
    #         form.save()
    #         form = SendMessage()
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

def login_view(request:HttpRequest):
    if request.user.is_authenticated:
        return redirect('chat_home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('group_selection')
        else:
            messages.error(request, 'Incorrect username and password combination')
    return render(request, 'login.html')



def logout_view(request:HttpRequest):
    logout(request)
    return redirect('login')

def group_selection_view(request:HttpRequest):
    return render(request, 'group_selection.html')

def registration_view(request:HttpRequest):
    if request.user.is_authenticated:
        return redirect('group_selection')
    
    form = Create_User_Form(request.POST)

    if form.is_valid():
        form.save()

        return redirect('group_selection')
    else:
        messages.info(request, form.errors)

    return render(request, 'registration.html', {'form':form})