
from django.db import models
from django.contrib.auth.models import User


class Feed(models.Model):
    title = models.CharField(max_length=20)

    url = models.CharField(max_length=100)
    last_changed = models.DateField()

    feed = models.FileField(upload_to='feeds')
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.title
