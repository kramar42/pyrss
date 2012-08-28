
from django.db import models
from django.contrib.auth.models import User


class Feed(models.Model):
    # For displaying in list of feeds
    title = models.CharField(max_length=100)

    # For checking equality of feeds
    url = models.CharField(max_length=100)
    # For checking time to refresh of feed
    time = models.DateField()

    # User foreign key
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.title


class Entry(models.Model):
    # For displaying in list of Entries
    title = models.CharField(max_length=100)
    # The same
    description = models.CharField(max_length=500)

    # For displaying entry
    entry = models.FileField(upload_to='entries')

    # Feed foreign key
    feed = models.ForeignKey(Feed)

    def __unicode__(self):
        return self.title
