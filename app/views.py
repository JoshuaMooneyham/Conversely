from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, Http404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import *
from app.forms import *


# Create your views here.
@login_required(login_url='login')
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

@login_required(login_url='login')
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
    print(profile)
    return render(request, "profile.html", context)

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
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

def login_view(request:HttpRequest):
    if request.user.is_authenticated:
        if 'just_signed_up' in request.session:
            del request.session['just_signed_up']
            return redirect('profile-config')
        else:
            return redirect('group_selection')

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

@login_required(login_url='login')
def logout_view(request:HttpRequest):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def group_selection_view(request:HttpRequest):
    return render(request, 'group_selection.html')


def registration_view(request: HttpRequest):    
    if request.method == 'POST':
        form = Create_User_Form(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['just_signed_up'] = True
                return redirect('profile-config')
            else:
                messages.error(request, "Failed to log in. Please try again.")
        else:
            messages.info(request, form.errors)
    else:
        form = Create_User_Form()

    return render(request, 'registration.html', {'form': form})

@login_required(login_url='login')
def make_profile_view(request: HttpRequest):
    if request.method == 'POST':
        form = Make_Profile_Form(request.POST)
        if form.is_valid():
            screen_name = form.cleaned_data['screen_name']
            image = form.cleaned_data['image']
            create_user_profile(request.user, screen_name, image)
            return redirect('group_selection')
    else:
        form = Make_Profile_Form()

    return render(request, 'make_profile.html', {'form': form})

@login_required(login_url='login')
def edit_profile_view(request:HttpRequest):
    user_profile = UserProfile.objects.get(user = request.user)
    user = User.objects.get(username = request.user)

    if request.method == 'POST':
        screen_name = user_profile.screen_name if not request.POST.get('screen_name') else request.POST.get('screen_name')
        email = user.email if not request.POST.get('new_email') else request.POST.get('new_email')
        image = request.FILES.get('image', user_profile.image)

        if 'update' in request.POST:
            
            update_profile_info(user_profile, screen_name, image)
            update_user_email(user, email)
            return redirect('group_selection')
        
        elif 'delete' in request.POST:
            delete_user_profile(request.user)
            return redirect('login')
        
    return render(request, 'update_profile.html', {'user':user})