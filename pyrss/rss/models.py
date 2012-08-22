from django.db import models


class User(models.Model):
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name


class Feed(models.Model):
    title = models.CharField(max_length=20)
    feed = models.FileField(upload_to='feeds/%d')
    user = models.ForeignKey(User)
