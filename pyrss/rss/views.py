
from rss.models import User, Feed
from django.http import render_to_response
import feedparser


def index(request):
    users = User.objects.all()

    return render_to_response('index.html', {'users': users})


def detail(request, user_id):
    user = User.objects.filter(id=user_id)[0]
    feeds = Feed.objects.filter(user=user)

    return render_to_response('detail.html', {'user': user, 'feeds': feeds})


def feed(request, feed_id):
    feed = Feed.objects.filter(id=feed_id)[0]
    title = feed.title
    feed = feedparser.parse(feed.feed)
    entries = feed.entries

    return render_to_response('feed.html', {'title': title, 'entries': entries})
