from django.forms import widgets
from rest_framework import serializers
from main.models import Utilisateur, Jeu, Serveur

class UtilisateurSerializer(serializers.Serializer):
    
    class Meta:
        model = Utilisateur
        fields = ('id', 'username', 'prenom', 'nom', 'email', 'active')
