from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from main.models import User, Game, Server
from main.serializers import UserSerializer, GameSerializer, ServerSerializer

models = {
   'users'  :(User, UserSerializer),
   'games'  :(Game, GameSerializer),
   'servers':(Server, ServerSerializer)
}

def get_model(key):
    try:
        model = models[key]
    except KeyError:
        model = 'null'
    return model
    
def home(request):
    return HttpResponse('<img src="http://a.pomf.se/lbvmhf.jpg" />')

class JSONResponse(HttpResponse):

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
        
@csrf_exempt
def models_list(request, key):
    
    model = get_model(key)
    if(model == 'null'):
        return HttpResponse(status=404)
    
    if request.method == 'GET':
        objects = model[0].objects.all()
        serializer = model[1](objects, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = model[1](data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)
        
@csrf_exempt
def models_detail(request, key, pk):

    model = get_model(key)
    if(model == 'null'):
        return HttpResponse(status=404)
    try:
        object_ = model[0].objects.get(pk=pk)
    except object_.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = model[1](user)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = model[1](user, data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        return JSONResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        object_.delete()
        return HttpResponse(status=204)
