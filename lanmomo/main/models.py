from django.db import models


class Utilisateur(models.Model):
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    username = models.CharField(max_length=30)
    email = models.CharField(max_length=256)


class Event(models.Model):
    places = models.IntegerField()
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    location = models.CharField(max_length=200)


class Jeu(models.Model):
    event = models.ForeignKey(Event)
    nom = models.CharField(max_length=100)
    description = models.CharField(max_length=500)


class Serveur(models.Model):
    jeu = models.ForeignKey(Jeu)
    adresse = models.CharField(max_length=20)
    port = models.IntegerField()
    places = models.IntegerField()
    modes = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
