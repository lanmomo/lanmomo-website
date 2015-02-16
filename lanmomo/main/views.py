from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from main.models import Utilisateur
from main.serializers import UtilisateurSerializer


def home(request):
    return HttpResponse('<img src="http://a.pomf.se/lbvmhf.jpg" />')



class JSONResponse(HttpResponse):

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
        
@csrf_exempt
def utilisateur_list(request):
    if request.method == 'GET':
        utilisateurs = Utilisateur.objects.all()
        serializer = UtilisateurSerializer(utilisateurs, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UtilisateurSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def utilisateur_detail(request, pk):
    try:
        utilisateur = Utilisateur.objects.get(pk=pk)
    except utilisateur.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = UtilisateurSerializer(utilisateur)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = UtilisateurSerializer(utilisateur, data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        return JSONResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        utilisateur.delete()
        return HttpResponse(status=204)
