from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
   url(r'^user/$', 'rss.views.index'),
   url(r'^user/(?P<user_id>\d+)/$', 'rss.views.detail'),
   url(r'^feed/(?P<feed_id>\d+)/$', 'rss.views.feed'),
)
