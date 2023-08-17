from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.utils.timezone import now
from .models import Train, Route, Booking, Comment, Journey
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import CommentForm, BookingForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse


def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')


class TrainCreate(CreateView):
    model = Train
    fields = ['name', 'railway', 'capacity', 'cars']
    template_name = 'train/train_form.html'


def train_index(request):
    trains = Train.objects.all()
    return render(request, 'train/index.html', {
        'trains': trains
    })


def train_detail(request, train_id):
    train = Train.objects.get(id=train_id)
    comments = train.comment_set.all()
    form = CommentForm()

    return render(request, 'train/train_detail.html', {'train': train, 'comments': comments, 'form': form})


class CommentUpdate(UpdateView):
    model = Comment
    fields = ['content', 'rating']
    template_name = 'comment/edit_comment.html'


def update_comment(request, pk):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        comment = get_object_or_404(Comment, id=pk)
        if form.is_valid():
            if not comment.user == request.user:
                error_msg = "You are not allowed to edit this comment, because it does not belong to you"
                return render(request, 'comment/edit_comment.html', {'form': form, 'comment': comment, 'error': error_msg})
            comment.content = request.POST.get('content')
            comment.rating = request.POST.get('rating')
            comment.date = now()
            comment.save()
            return redirect(reverse('train_detail', kwargs={'train_id': comment.train.id}))
        else:
            error_msg = 'Invalid values'
            return render(request, 'comment/edit_comment.html', {'form': form, 'comment': comment, 'error': error_msg})

    else:
        comment = get_object_or_404(Comment, id=pk)
        comment_dict = {'content': comment.content, 'rating': comment.rating}
        form = CommentForm(comment_dict)
        return render(request, 'comment/edit_comment.html', {'form': form, 'comment': comment})


class CommentDelete(DeleteView):
    model = Comment
    template_name = 'comment/confirm_comment_delete.html'
    success_url = 'https://www.subway.com/en-us?utm_source=bing&utm_medium=cpc&utm_term=subway%20com_exact&utm_content=brand&utm_campaign=&cid=0:0:00:0:nat-us:0&0=0&gclid=eda71fd3e2d01efd63ec7b08791cf243&gclsrc=3p.ds&msclkid=eda71fd3e2d01efd63ec7b08791cf243'


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)


@login_required
def add_comment(request, train_id):
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.train = get_object_or_404(Train, id=train_id)
        comment.save()

        return redirect('train_detail', train_id=train_id)

def journey_index(request):
    journeys = Journey.objects.all()
    return render(request, 'journey/journey.html', {
        'journeys': journeys
    })

def journey_detail(request, journey_id):
    journey = get_object_or_404(Journey, id=journey_id)
    stops = journey.route.stationorder_set.all()
    return render(request, 'journey/journey_detail.html', {'journey': journey, "stops": stops})

@login_required
def create_booking(request, journey_id):
    user = request.user
    journey = Journey.objects.get(id=journey_id)
    fields = {'journey':journey, 'user':user}
    booking = BookingForm(fields)
    stops = journey.route.stationorder_set.all()
    if request.method == "GET":
        return render(request, 'booking/booking.html', {'booking': booking, 'journey':journey, 'stops':stops})
    else :
        form = BookingForm(request.POST)
        booking = form.save(commit=False)
        booking.journey = journey
        if form.is_valid():
            booking.save()
            return redirect('booking/my_bookings.html')
        return render(request, 'booking/booking.html', {'booking': booking, 'journey':journey, 'stops':stops, 'error':'invalid values'})


