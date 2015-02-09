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
    endroit = models.CharField(max_length=200)


class Jeu(models.Model):
    event = models.ForeignKey(Event)
    nom = models.CharField(max_length=100)
    description = models.CharField(max_length=500)


class Serveur(models.Model):
    jeu = models.ForeignKey(Jeu)
    # ipv4, ipv6 ou nom de domaine
    adresse = models.CharField(max_length=60)
    port = models.IntegerField()
    places = models.IntegerField()
    mode = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
