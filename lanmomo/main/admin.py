from django.contrib import admin
from main.models import User, Game, Server, Event

admin.site.register(User)
admin.site.register(Game)
admin.site.register(Server)
admin.site.register(Event)

