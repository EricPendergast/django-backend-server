from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route

import mongoengine

from eledata.models.users import User, Group
from eledata.models.analysis_questions import GroupAnalysisSettings

from eledata.verifiers.users import CreateUserVerifier, LoginVerifier
from eledata.util import InvalidInputError, from_json, to_json

from project import settings

# We can use native django authentication because it dierctly makes use of the
# mongoengine authentication backend set in the settings.
from django.contrib.auth import authenticate, logout
from eledata.auth import login, CustomLoginRequiredMixin


class UserIndexViewSet(CustomLoginRequiredMixin, viewsets.ViewSet):
    @list_route(methods=['get'])
    def index(self, request):
        request.user.counter += 1
        
        request.user.group.counter += 1
        request.user.group.save()
        request.user.save()
        
        return Response("User counter: %s,  Group counter: %s" % (request.user.counter, request.user.group.counter))

class UserViewSet(viewsets.ViewSet):
    
    #Maybe TODO: Create update_questions method. Looks at the json questions file and updates all user groups to match the file.
    #TODO: Should creating a user with a nonexistant group create a new group or throw an error?
    
    
    #TODO: Handle the case of creating a user that already exists
    @list_route(methods=['post'])
    def create_user(self, request):
        verifier = CreateUserVerifier()
        verifier.verify(0, request.data)
        
        username = request.data['username']
        password = request.data['password']
        group_name = request.data['group']
        
        if User.objects(username=username).only('username').limit(1):
            raise InvalidInputError("A user with this name already exists")
        
        user = User.create_user(username, password)
        try:
            group = Group.objects.get(name=group_name)
        except mongoengine.DoesNotExist:
            group = Group(name=group_name)
            group.analysis_settings = \
                    GroupAnalysisSettings(**settings.CONSTANTS['analysis_settings'])
            group.save()
        
        user.group = group
        user.save()
        
        assert verifier.verified
        return Response("Created user %s" % user.username)
        
    
        
    @list_route(methods=['post'])
    def login(self, request):
        verifier = LoginVerifier()
        verifier.verify(0, request.data)
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        
        if user is not None:
            request.session.set_expiry(60 * 60)
            login(request, user)
            return Response({"username": user.username, "message": "Login successful"})

        else:
            return Response({"error": "Login failed"}, status=403)
    
    
    
    @list_route(methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({"message": "Logged out"})
