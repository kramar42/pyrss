
from django.shortcuts import HttpResponse, render_to_response, redirect
#from django.shortcuts import render

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.core.files import File

from urllib import urlretrieve
from datetime import datetime, timedelta

import feedparser
import os

from rss.models import Feed, Entry
#from rss.forms import LoginForm


def login_view(request):
    """
    Login view.
    Using login.html template.

    Trying to get from GET login parametrs and login.
    Then authenticate, login and redirect to /feeds.

    If there is no GET - display simple login page.
    """

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
    """
    Register view.
    Using register.html template.

    Working the same as login_view.
    """

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
                return render_to_response('register.html', {'result': 'user'})
        else:
            # Passwords veren't equal
            return render_to_response('register.html', {'result': 'false'})
    except KeyError:
        # Or display simple register page
        return render_to_response('register.html')


@login_required
def logout_view(request):
    """
    Logout view.
    Simple log's user out.

    Redirects to /login.
    """

    logout(request)
    return redirect('/login')


@login_required
def feeds(request, page='1'):
    """
    Feeds view.
    Using feeds.html template.

    Displaying all feeds.
    """

    __time_update(request.user)

    feeds = Feed.objects.filter(user=request.user)

    bottom = (int(page) - 1) * 10
    top = bottom + 10

    prev = 'none' if page == '1' else \
           'none' if len(feeds[bottom - 1: bottom]) == 0 else \
           int(page) - 1

    next = 'none' if len(feeds[top: top + 1]) == 0 else \
           int(page) + 1

    return render_to_response('feeds.html', {
        'username': request.user.username,
        'feeds': feeds[bottom: top],
        'prev': prev, 'next': next})


@login_required
def add_feed(request):
    """
    Add feed view.
    Using add_feed.html temlate.

    Trying to get URL from post.
    If we couldn't - redirecting back to add_feed.html page.

    Trying to get Feed object with such URL.
    If we coult - redirecting to message page.

    Then calculate Feed's
        Title, URL, Time, Feed, User fields
    and create (& save) Feed object.

    Add entries.

    Redirects to /feeds.
    """

    __time_update(request.user)

    try:
        url = request.POST['url']
        if not url.startswith('http://'):
            url = 'http://' + url
    except KeyError:
        return render_to_response('add_feed.html',
            {'username': request.user.username})

    try:
        Feed.objects.get(url=url, user=request.user)
        return render_to_response('message.html', {'message':
            'There is already such feed',
            'back': '/feeds'})
    except Feed.DoesNotExist:
        pass

    feed = feedparser.parse(url)

    # If were errors loading XML
    try:
        # Title field in Feed
        title = feed.feed.title
    except AttributeError:
        # Display warning message
        return render_to_response('message.html', {'message':
            'Wrong feed URL or connection Error.',
            'back': '/add_feed'})

    # Time field in Feed
    time = datetime.now()

    # Create Feed and save it
    feed_obj = Feed(title=title, url=url, time=time,
        user=request.user)
    feed_obj.save()

    __add_entries(feed.entries, feed_obj)

    return redirect('/feeds')


@login_required
def feed(request, feed_id, page='1'):
    """
    Feed view.
    Using feed.html template.

    Displaying feed's entries.
    """

    __time_update(request.user)

    try:
        feed = Feed.objects.get(user=request.user, id=feed_id)
        title = feed.title
        entries = Entry.objects.filter(feed=feed)
    except:
        return render_to_response('message.html', {'message':
            'There is no such feed.',
            'back': '/feeds'})

    bottom = (int(page) - 1) * 5
    top = bottom + 5

    prev = 'none' if page == '1' else \
           'none' if len(entries[bottom - 1: bottom]) == 0 else \
           int(page) - 1

    next = 'none' if len(entries[top: top + 1]) == 0 else \
           int(page) + 1

    feeds = Feed.objects.filter(user=request.user)

    return render_to_response('feed.html', {
        'username': request.user.username,
        'feed_id': int(feed_id), 'feeds': feeds,
        'title': title, 'entries': entries[bottom: top],
        'prev': prev, 'next': next})


@login_required
def entry(request, entry_id):
    """
    Entry view.
    Using entry.html template.

    Displaying entry's content using local file.
    """

    __time_update(request.user)

    try:
        entry = Entry.objects.get(id=entry_id)
        feed = entry.feed

        if feed.user == request.user:
            entry = entry.entry.read()
        else:
            return render_to_response('message.html', {'message':
                'There is no such entry.',
                'back': '/feeds'})
    except:
        return render_to_response('message.html', {'message':
            'Error opening entry file! Please, reload feed.',
            'back': '/feeds'})

    return HttpResponse(entry)


@login_required
def update_feed(request, feed_id):
    """
    Update feed view.
    Using update_feed.html template.

    Manually updates feed entires.

    Redirects to /feeds.
    """

    __time_update(request.user)

    try:
        feed = Feed.objects.get(id=feed_id, user=request.user)
    except Feed.DoesNotExist:
        return render_to_response('message.html',
            {'message': 'There is no such feed.',
            'back': '/feeds'})

    __update_feed(feed)
    return redirect('/feeds')


@login_required
def modify_feed(request, feed_id):
    """
    Modify feed view.
    Using modify_feed.html temlpate.

    You can modify feed object using simple form.

    Redirects to /feeds.
    """

    __time_update(request.user)

    try:
        feed = Feed.objects.get(id=feed_id, user=request.user)
    except KeyError:
        return render_to_response('message.html',
            {'message': 'There is no such feed.',
            'back': '/feeds'})

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
        return render_to_response('modify_feed.html',
            {'feed': feed,
            'username': request.user.username})


@login_required
def delete_feed(request, feed_id):
    """
    Delete feed view.
    Using delete_feed.html template.

    Simple deletes feed and all entry objects.

    Redirects to /feeds.
    """

    __time_update(request.user)

    try:
        Feed.objects.get(id=feed_id, user=request.user).delete()
    except:
        pass

    return redirect('/feeds')


@login_required
def search(request):
    """
    Search view.
    Using search.html temlplate.

    Simple search using filter.
    """

    try:
        q = request.GET['q']
        result = Entry.objects.filter(title__contains=q)

        return render_to_response('search.html',
            {'result': result,
            'username': request.user.username})
    except KeyError:
        return render_to_response('search.html',
            {'username': request.user.username})


def __update_feed(feed_obj):
    """
    Private update feed func.
    Manually updates feed.
    """

    url = feed_obj.url
    feed = feedparser.parse(url)

    try:
        feed.feed.title
    except AttributeError:
        return

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
    """
    Private time update func.
    Updates feed after some time.
    """

    feeds = Feed.objects.filter(user=user)

    for feed in feeds:
        # Last time updated more than 5 minutes ago
        if (datetime.now() - feed.time) > timedelta(0, 300, 0):
            __update_feed(feed)


def __add_entries(entries, feed):
    """
    Private add entries func.

    Adds entries to a feed without repeating them.
    Don't downloads entry, if there is entry with such title
        from another feed. Instead it uses that entry.
    """

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
            entry_obj = Entry(title=e.title,
                description=e.description,
                entry=e.entry, feed=feed)
            entry_obj.save()
        # Or create new Entry from scratch
        else:
            entry_name = entry.title + '.html'
            # If bad link or entry name
            try:
                urlretrieve(entry.link, entry_name)

                entry_file = open(entry_name)
                entry_file = File(entry_file)

                entry_obj = Entry(title=entry.title,
                    description=entry.description,
                    entry=entry_file, feed=feed)
                entry_obj.save()

                os.remove(entry_name)
            except:
            # Go to next entry
                continue
