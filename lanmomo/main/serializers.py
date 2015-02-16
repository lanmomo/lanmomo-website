from django.forms import widgets
from rest_framework import serializers
from main.models import User, Game, Server

class UserSerializer(serializers.Serializer):
    
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'active')
