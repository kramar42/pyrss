
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Views, working with User
    url(r'^$', 'rss.views.login_view'),
    url(r'^login/$', 'rss.views.login_view'),
    url(r'^register/$', 'rss.views.register_view'),
    url(r'^logout/$', 'rss.views.logout_view'),

    # List of all feeds by User
    url(r'^feeds/$', 'rss.views.feeds'),
    url(r'^add_feed/$', 'rss.views.add_feed'),

    # Views, that display feed/entry
    url(r'^feed/(?P<feed_id>\d+)/$', 'rss.views.feed'),
    url(r'^entry/(?P<entry_id>\d+)/$', 'rss.views.entry'),

    url(r'^update_feed/(?P<feed_id>\d+)/$', 'rss.views.update_feed'),
    url(r'^modify_feed/(?P<feed_id>\d+)/$', 'rss.views.modify_feed'),
    url(r'^delete_feed/(?P<feed_id>\d+)/$', 'rss.views.delete_feed'),
)
