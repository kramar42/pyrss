
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^login/$', 'rss.views.login_view'),
    url(r'^register/$', 'rss.views.register_view'),
    url(r'^logout/$', 'rss.views.logout_view'),

    url(r'^feeds/$', 'rss.views.feeds'),
    url(r'^add_feed/$', 'rss.views.add_feed'),
    url(r'^feed/(?P<feed_id>\d+)/$', 'rss.views.feed'),
)
