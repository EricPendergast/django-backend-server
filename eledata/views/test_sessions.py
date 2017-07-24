from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route

import users.views
from users.models import UserImpl, Token

class SessionTestViewSet(viewsets.ViewSet):
    
    @list_route(methods=['get'])
    def index(self, request):
        user = Token.objects.get(key=request.session['token']).user
        user.counter += 1
        user.save()
        
        return Response(str(user.counter))
    
    @list_route(methods=['post'])
    def create_user(self, request):
        username = request.data['username']
        password = request.data['password']
        
        user = UserImpl.create_user(username, password)
        
        return Response("Created user %s" % user)
        
    @list_route(methods=['post'])
    def login(self, request):
        user = UserImpl.objects.get(username=request.data['username'])
        if not user.check_password(request.data['password']):
            return Response("incorrect password")
        
        token = Token(user=user)
        token.save()
        
        request.session['token'] = token.key
        
        return Response("Success")
