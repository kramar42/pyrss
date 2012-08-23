
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files import File
from datetime import datetime

from rss.models import Feed

from urllib import urlretrieve
from os import remove
import feedparser


def login_view(request):
    try:
        next = request.GET['next']
        return render_to_response('login.html', {'next': next})
    except:
        pass

    try:
        username = request.POST['login']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/feeds')
            else:
                return render_to_response('login.html', {'disabled': 'true'})
        else:
            return render_to_response('login.html', {'invalid': 'true'})
    except KeyError:
        return render_to_response('login.html')


def register_view(request):
    try:
        name = request.POST['username']
        psk1 = request.POST['psk1']
        psk2 = request.POST['psk2']

        if psk1 == psk2:
            user = User.objects.create_user(name, '', psk1)
            user = authenticate(username=name, password=psk1)
            login(request, user)
            return redirect('/feeds')
        else:
            return render_to_response('register.html', {'result': 'false'})
    except KeyError:
        return render_to_response('register.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('/login')


@login_required
def feeds(request):
    feeds = Feed.objects.filter(user=request.user)

    return render_to_response('feeds.html', {'feeds': feeds})


@login_required
def add_feed(request):
    try:
        url = request.POST['url']
        rss_name = url.split('/')[-1]
        urlretrieve(url, rss_name)

        feed = feedparser.parse(rss_name)

        feed_file = open(rss_name)
        feed_file = File(feed_file)

        feed = Feed(title=feed.feed.title, url=url, \
            last_changed=datetime.now(), \
            feed=feed_file, user=request.user)
        feed.save()
        remove(rss_name)

        return redirect('/feeds')
    except KeyError:
        return render_to_response('add_feed.html')


@login_required
def feed(request, feed_id):
    try:
        feed = Feed.objects.get(user=request.user, id=feed_id)

        feed = feedparser.parse(feed.feed)
        title = feed.feed.title
        entries = feed.entries
    except:
        title = entries = 'false'

    return render_to_response('feed.html', {'title': title, 'entries': entries})
