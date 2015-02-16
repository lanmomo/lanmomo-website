from django.forms import widgets
from rest_framework import serializers
from main.models import User, Game, Server

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',
                  'email', 'active')


class GameSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Game
        fields = ('id', 'name', 'description')
    

class ServerSerializer(serializers.ModelSerializer):
    
    class Meta :   
        model = Server
        fields = ('id', 'game', 'ip_addr', 'port',
                  'slots', 'mode', 'description')
