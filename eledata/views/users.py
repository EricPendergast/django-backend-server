from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route

import mongoengine

from eledata.models.users import User, Token, Group

# We can use native django authentication because it dierctly makes use of the
# mongoengine authentication backend set in the settings.
from django.contrib.auth import authenticate
from eledata.auth import login, get_user

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

    
class UserIndexViewSet(viewsets.ViewSet):
    
    @method_decorator(login_required)
    @list_route(methods=['get'])
    def index(self, request):
        if not request.user.is_authenticated():
            return Response("User not authenticated")
        # user = Token.objects.get(key=request.session['session_id']).user
        # user = authenticate(session_id=request.session['session_id'])
        user = request.user
        user.counter += 1
        
        user.group.counter += 1
        user.group.save()
        user.save()
        
        return Response("User counter: %s,  Group counter: %s" % (user.counter, user.group.counter))

class UserViewSet(viewsets.ViewSet):
    
    #TODO: Move questions from their own database to being embedded in user groups
    #TODO: Create server side json file that contains all questions
    #Maybe TODO: Create update_questions method. Looks at the json questions file and updates all user groups to match the file.
    
    
    @list_route(methods=['post'])
    def create_user(self, request):
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
        
        return Response("Created user %s" % user.username)
        
    @list_route(methods=['post'])
    def login(self, request):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        
        if user is not None:
            request.session.set_expiry(30)
            login(request, user)
        else:
            return Response("Login failed")
            
        
        # token = Token(user=user)
        # token.save()
        
        # request.session['session_id'] = token.key
        
        return Response("Login successful")
