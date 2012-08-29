
from django.shortcuts import HttpResponse, render_to_response, redirect

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.core.files import File

from urllib import urlretrieve
from datetime import datetime, timedelta

import feedparser
import os

from rss.models import Feed, Entry


def login_view(request):
    try:
        # If we were redirected from another page
        next = request.GET['next']
        # Print message
        return render_to_response('login.html', {'next': next})
    except:
        pass

    try:
        username = request.POST['login']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                # All is cool
                login(request, user)
                return redirect('/feeds')
            else:
                # User is disabled
                return render_to_response('login.html', {'disabled': 'true'})
        else:
            # Invalid user
            return render_to_response('login.html', {'invalid': 'true'})
    except KeyError:
        # Or just display the login
        return render_to_response('login.html')


def register_view(request):
    try:
        name = request.POST['username']
        psk1 = request.POST['psk1']
        psk2 = request.POST['psk2']

        if psk1 == psk2:
            try:
                # Create new User, authenticate and login
                User.objects.create_user(name, '', psk1)
                user = authenticate(username=name, password=psk1)
                login(request, user)

                return redirect('/feeds')
            except:
                return render_to_response('message.html', {'message': \
                    'There are user with such name. Choose another.'})
        else:
            # Passwords veren't equal
            return render_to_response('register.html', {'result': 'false'})
    except KeyError:
        # Or display simple register page
        return render_to_response('register.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('/login')


@login_required
def feeds(request):
    __time_update(request.user)

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
    and create (& save) Feed object.

    Add entries.
    """
    __time_update(request.user)

    try:
        url = request.POST['url']
        if not url.startswith('http://'):
            url = 'http://' + url
    except KeyError:
        return render_to_response('add_feed.html')

    try:
        Feed.objects.get(url=url, user=request.user)
        return render_to_response('message.html', {'message': \
            'There is already such feed'})
    except Feed.DoesNotExist:
        pass

    feed = feedparser.parse(url)

    # If were errors loading XML
    try:
        # Title field in Feed
        title = feed.feed.title
    except AttributeError:
        # Display warning message
        return render_to_response('message.html', {'message': \
            'Wrong feed URL.'})

    # Time field in Feed
    time = datetime.now()

    # Create Feed and save it
    feed_obj = Feed(title=title, url=url, time=time, \
        user=request.user)
    feed_obj.save()

    __add_entries(feed.entries, feed_obj)

    return redirect('/feeds')


@login_required
def feed(request, feed_id):
    __time_update(request.user)

    try:
        feed = Feed.objects.get(user=request.user, id=feed_id)
        title = feed.title
        entries = Entry.objects.filter(feed=feed)
    except:
        title = entries = 'false'

    return render_to_response('feed.html', {'title': title, 'entries': entries})


@login_required
def entry(request, entry_id):
    __time_update(request.user)

    try:
        entry = Entry.objects.get(id=entry_id)
        feed = entry.feed

        if feed.user == request.user:
            entry = entry.entry.read()
        else:
            entry = 'false'
    except:
        entry = 'false'

    return HttpResponse(entry)


@login_required
def update_feed(request, feed_id):
    __time_update(request.user)

    try:
        feed = Feed.objects.get(id=feed_id, user=request.user)
    except Feed.DoesNotExist:
        return render_to_response('message.html', \
            {'message': 'There is no such feed.'})

    __update_feed(feed)
    return redirect('/feeds')


@login_required
def modify_feed(request, feed_id):
    __time_update(request.user)

    try:
        feed = Feed.objects.get(id=feed_id, user=request.user)
    except KeyError:
        return render_to_response('message.html', \
            {'message': 'There is no such feed.'})

    # Try to get data from form & update feed
    try:
        title = request.POST['title']
        url = request.POST['url']

        feed.title = title
        feed.url = url

        feed.save()
        return redirect('/feeds')
    # Or display new form, filled with current feed values
    except KeyError:
        return render_to_response('modify_feed.html', {'feed': feed})


@login_required
def delete_feed(request, feed_id):
    __time_update(request.user)

    try:
        Feed.objects.get(id=feed_id, user=request.user).delete()
    except:
        pass

    return redirect('/feeds')


def __update_feed(feed_obj):
    url = feed_obj.url
    feed = feedparser.parse(url)

    # List of new entries in downloaded XML
    new_entries = feed.entries
    new_entries_titles = [entry.title for entry in new_entries]

    # List of current entries in database
    old_entries = Entry.objects.filter(feed=feed_obj)
    old_entries_titles = [entry.title for entry in old_entries]

    # Check what old entries arn't in new entries
    # They will be deleted
    for entry_title in old_entries_titles:
        if entry_title not in new_entries_titles:
            Entry.objects.get(title=entry_title, feed=feed_obj).delete()

    # Add all new entries
    __add_entries(new_entries, feed_obj)

    # Update time and save
    feed_obj.time = datetime.now()
    feed_obj.save()


def __time_update(user):
    feeds = Feed.objects.filter(user=user)

    for feed in feeds:
        # Last time updated more than 5 minutes ago
        if (datetime.now() - feed.time) > timedelta(0, 300, 0):
            __update_feed(feed)


def __add_entries(entries, feed):
    for entry in entries:
        try:
            # If there is entry with such title in this feed
            Entry.objects.get(title=entry.title, feed=feed)
            continue
        except Entry.DoesNotExist:
            pass

        # Try to find another entries with such title
        e = Entry.objects.filter(title=entry.title)
        # If found
        if len(e) != 0:
            e = e[0]
            # Copy all containing
            entry_obj = Entry(title=e.title, \
                description=e.description, \
                entry=e.entry, feed=feed)
            entry_obj.save()
        # Or create new Entry from scratch
        else:
            entry_name = entry.title + '.html'
            # If bad link or entry name
            try:
                urlretrieve(entry.link, entry_name)
            except IOError:
            # Go to next entry
                continue

            entry_file = open(entry_name)
            entry_file = File(entry_file)

            entry_obj = Entry(title=entry.title, \
                description=entry.description, \
                entry=entry_file, feed=feed)
            entry_obj.save()

            os.remove(entry_name)
