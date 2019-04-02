from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone


class Capsule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='static')
    title = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    content = models.TextField()
    place = models.ForeignKey('Place', on_delete=models.CASCADE)
    views = models.IntegerField(default=0, blank=True)
    # 1 image, 2 video, 3 audio, 4 other
    category = models.IntegerField()
    address = models.CharField(max_length=250, blank=True)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    capsule = models.ForeignKey(Capsule, on_delete=models.CASCADE, blank=True)

    class Meta:
        unique_together = ('user', 'capsule')


class Playlist(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    capsules = models.ManyToManyField('Capsule')
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class PlaylistOrder(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    capsule = models.ForeignKey(Capsule, on_delete=models.CASCADE)
    position = models.IntegerField()


class Place(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="static")

    def __str__(self):
        return self.name

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(null=False)
    is_visible = models.BooleanField(default=True)
    capsule = models.ForeignKey('Capsule', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to="static", blank=True, null=True)
    city = models.CharField(max_length=256)

class Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField(default=0, blank=True)
