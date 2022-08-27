from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.http import HttpResponse


# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'lets learn python'},
#     {'id': 2, 'name': 'lets learn C++'},
#     {'id': 3, 'name': 'lets learn java'},
#     {'id': 4, 'name': 'lets learn swift'},
# ]

def loginPage(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.object.get(username=username)
        except:
            messages.error(request, 'User not exist.')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials.')
    context = {'page': page}
    return render(request, 'myapp/login_form.html', context)


def logoutPage(request):
    logout(request)
    return redirect('home')


def register(request):
    form = UserCreationForm

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'registration failed')
    return render(request, 'myapp/login_form.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    room_count = rooms.count()
    topics = Topic.objects.all()
    room_message = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_message': room_message}
    return render(request, 'myapp/home.html', context)


def room(request, pk):
    rooms = Room.objects.get(pk=pk)
    roomMessages = rooms.message_set.all()
    participants = rooms.participant.all()

    if request.method == 'POST':
        messages = Message.objects.create(
            user=request.user,
            room=rooms,
            body=request.POST.get('body')
        )
        rooms.participant.add(request.user)
        return redirect('room', pk=rooms.id)

    context = {'room': rooms, 'roo_messages': roomMessages, 'participants': participants}
    return render(request, 'myapp/room.html', context)


# def room(request, pk):
#     roo = pythonmanage.py createNone
#     for i in rooms:
#         if i['id'] == int(pk):
#             roo = i
#     context = {'room': roo}
#     return render(request, 'myapp/room.html', context)
@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    topic = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')

        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()

    context = {'form': form, 'topics': topic}
    return render(request, 'myapp/room_form.html', context)


@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topic = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('Not allowed')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.name = request.POST.get('name'),
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect('home')
    context = {'form': form, 'topics': topic, 'room': room}
    return render(request, 'myapp/room_form.html', context)


@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Not allowed')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'myapp/delete.html', {'obj': room})


@login_required(login_url='/login')
def deleteMessage(request, pk):
    messages = Message.objects.get(id=pk)
    if request.user != messages.user:
        return HttpResponse('Not allowed')
    if request.method == 'POST':
        messages.delete()
        return redirect('home')
    return render(request, 'myapp/delete.html', {'obj': messages})


@login_required(login_url='/login')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    room_message = user.message_set.all()
    context = {'user': user, 'rooms': rooms, 'topics': topics, 'room_message': room_message}
    return render(request, 'myapp/profile.html', context)


@login_required(login_url='/login')
def updateProfile(request):

    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'myapp/update_user.html', context)
