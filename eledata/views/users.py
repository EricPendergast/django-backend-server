from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route

import mongoengine

from eledata.models.users import User, Group
from eledata.verifiers.users import CreateUserVerifier, LoginVerifier
from eledata.util import InvalidInputError

# We can use native django authentication because it dierctly makes use of the
# mongoengine authentication backend set in the settings.
from django.contrib.auth import authenticate, logout
from eledata.auth import login, CustomLoginRequiredMixin

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

    
class UserIndexViewSet(CustomLoginRequiredMixin, viewsets.ViewSet):
    @list_route(methods=['get'])
    def index(self, request):
        request.user.counter += 1
        
        request.user.group.counter += 1
        request.user.group.save()
        request.user.save()
        
        return Response("User counter: %s,  Group counter: %s" % (request.user.counter, request.user.group.counter))

class UserViewSet(viewsets.ViewSet):
    
    #TODO: Create server side json file that contains all questions
    #Maybe TODO: Create update_questions method. Looks at the json questions file and updates all user groups to match the file.
    #TODO: validate input
    #TODO: Should creating a user with a nonexistant group create a new group or throw an error?
    
    
    @list_route(methods=['post'])
    def create_user(self, request):
        try:
            verifier = CreateUserVerifier()
            verifier.verify(0, request.data)
            username = request.data['username']
            password = request.data['password']
            group_name = request.data['group']
            
            user = User.create_user(username, password)
            try:
                group = Group.objects.get(name=group_name)
            except mongoengine.DoesNotExist:
                group = Group(name=group_name)
                group.save()
            
            user.group = group
            user.save()
            
            assert verifier.verified
            return Response("Created user %s" % user.username)
        except InvalidInputError as e:
            #TODO: Turn this into a mixin
            return Response({"error":str(e)}, status=400)
        
    @list_route(methods=['post'])
    def login(self, request):
        try:
            verifier = LoginVerifier()
            verifier.verify(0, request.data)
            username = request.data['username']
            password = request.data['password']
            user = authenticate(username=username, password=password)
            
            if user is not None:
                request.session.set_expiry(30 * 30)
                login(request, user)
            else:
                return Response("Login failed", status=403)
                
            return Response("Login successful")
        except InvalidInputError as e:
            #TODO: Turn this into a mixin
            return Response({"error":str(e)}, status=400)
    
    @list_route(methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({"msg":"Logged out"})
