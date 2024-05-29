from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from app.models import *
from app.forms import *

# Create your views here.
def chat_view(req: HttpRequest, channel: str) -> HttpResponse:
    context = {}
    try:
        chatroom = Group.objects.get(name=channel)
    except: 
        pass
        # return redirect('home') # Send home if bad group request
    context["messages"] = chatroom.messages.all()
    form = SendMessage()
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
            return render(req, 'message_partial.html', {'message': newMessage, 'user': req.user})

    context["form"] = form
    return render(req, 'ChatHome.html', context)