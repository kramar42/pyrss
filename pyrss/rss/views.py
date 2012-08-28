
from django.shortcuts import HttpResponse, render_to_response, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.core.files import File

from urllib import urlretrieve
from datetime import datetime

import feedparser
import os

from rss.models import Feed, Entry


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
            User.objects.create_user(name, '', psk1)
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
    """
    Trying to get URL from post.
    If we couldn't - redirecting back to add_feed.html page.

    Trying to get Feed object with such URL.
    If we coult - redirecting to message page.

    Then calculate Feed's
        Title, URL, Time, Feed, User fields
    and create Feed object.


    """

    try:
        url = request.POST['url']
    except KeyError:
        return render_to_response('add_feed.html')

    try:
        Feed.objects.get(url=url)
        return render_to_response('message.html', {'message': 'There is such feed'})
    except Feed.DoesNotExist:
        pass

    feed = feedparser.parse(url)

    # Title field in Feed
    title = feed.feed.title

    # Time field in Feed
    time = datetime.now()

    # create Feed and save it
    feed_obj = Feed(title=title, url=url, time=time, \
        user=request.user)
    feed_obj.save()

    for entry in feed.entries:
        try:
            Entry.objects.get(title=entry.title)
            continue
        except Entry.DoesNotExist:
            pass

        # entry name to save
        entry_name = entry.title + '.html'
        urlretrieve(entry.link, entry_name)

        # Entry file field
        entry_file = open(entry_name)
        entry_file = File(entry_file)

        # create and save entry object
        entry_obj = Entry(title=entry.title, \
            description=entry.description, \
            entry=entry_file, feed=feed_obj)
        entry_obj.save()

        # remove tmp entry file
        os.remove(entry_name)

    return redirect('/feeds')


@login_required
def feed(request, feed_id):
    try:
        feed = Feed.objects.get(user=request.user, id=feed_id)
        title = feed.title
        entries = Entry.objects.filter(feed=feed)
    except:
        title = entries = 'false'

    return render_to_response('feed.html', {'title': title, 'entries': entries})


@login_required
def entry(request, entry_id):
    try:
        entry = Entry.objects.get(id=entry_id)
        entry = entry.entry.read()
    except:
        entry = 'false'

    return HttpResponse(entry)


@login_required
def update_feed(request, feed_id):
    pass
