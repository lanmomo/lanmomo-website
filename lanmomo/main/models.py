from django.db import models


class User(models.Model):
    username = models.CharField(max_length=30, default='anon')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=256)
    active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username


class Event(models.Model):
    seats = models.IntegerField()
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    location = models.CharField(max_length=200)
    attendees = models.ManyToManyField(User)

class Game(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.nom

class Server(models.Model):
    game = models.ForeignKey(Game)
    # ipv4, ipv6 ou nom de domaine
    ip_addr = models.CharField(max_length=200)
    port = models.IntegerField()
    slots = models.IntegerField()
    mode = models.CharField(max_length=200)
    description = models.TextField()

