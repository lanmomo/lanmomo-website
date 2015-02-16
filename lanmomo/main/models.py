from django.db import models


class Utilisateur(models.Model):
    username = models.CharField(max_length=30, default='anon')
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    email = models.CharField(max_length=256)
    active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username


class Event(models.Model):
    places = models.IntegerField()
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    endroit = models.CharField(max_length=200)
    participants = models.ManyToManyField(Utilisateur)

class Jeu(models.Model):
    event = models.ForeignKey(Event)
    nom = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.nom

class Serveur(models.Model):
    jeu = models.ForeignKey(Jeu)
    # ipv4, ipv6 ou nom de domaine
    adresse = models.CharField(max_length=200)
    port = models.IntegerField()
    places = models.IntegerField()
    mode = models.CharField(max_length=200)
    description = models.TextField()

