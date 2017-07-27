from mongoengine.django.auth import MongoEngineBackend
from eledata.models.users import Token

from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY, constant_time_compare, _get_backends, rotate_token, load_backend
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed

from project import settings

#TODO: should I use the name token or session_id?
class CustomAuthBackend(MongoEngineBackend):
    def authenticate(self, username=None, password=None):
        if username is not None and password is not None:
            return super(CustomAuthBackend, self).authenticate(username=username, password=password)
        elif session_id is not None:
            try:
                token = Token.objects.get(key=session_id)
            except Token.DoesNotExist:
                raise exceptions.AuthenticationFailed('Invalid token.')

            if not token.user.is_active:
                raise exceptions.AuthenticationFailed('User inactive or deleted.')

            return token.user
        else:
            raise exceptions.AuthenticationFailed('Not enough information')
            


#########################################################
#  Mostly Copied from /django/contrib/auth/__init__.py  #
#  A few lines are changed so that it works with        #
#  mongoengine users                                    #
#########################################################
from bson.objectid import ObjectId
def _get_user_session_key(request):
    # This value in the session is always serialized to a string, so we need
    # to convert it back to Python whenever we access it.
    return ObjectId(request.session[SESSION_KEY])

def login(request, user, backend=None):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request. Note that data set during
    the anonymous session is retained when the user logs in.
    """
    session_auth_hash = ''
    if user is None:
        user = request.user
    if hasattr(user, 'get_session_auth_hash'):
        session_auth_hash = user.get_session_auth_hash()

    if SESSION_KEY in request.session:
        if _get_user_session_key(request) != user.pk or (
                session_auth_hash and
                not constant_time_compare(request.session.get(HASH_SESSION_KEY, ''), session_auth_hash)):
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()

    try:
        backend = backend or user.backend
    except AttributeError:
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            raise ValueError(
                'You have multiple authentication backends configured and '
                'therefore must provide the `backend` argument or set the '
                '`backend` attribute on the user.'
            )

    request.session[SESSION_KEY] = str(user.pk)#user._meta.pk.value_to_string(user)
    request.session[BACKEND_SESSION_KEY] = backend
    request.session[HASH_SESSION_KEY] = session_auth_hash
    if hasattr(request, 'user'):
        request.user = user
    rotate_token(request)
    user_logged_in.send(sender=user.__class__, request=request, user=user)


def get_user(request):
    """
    Returns the user model instance associated with the given request session.
    If no user is retrieved an instance of `AnonymousUser` is returned.
    """
    user = None
    try:
        user_id = _get_user_session_key(request)
        backend_path = request.session[BACKEND_SESSION_KEY]
    except KeyError:
        pass
    else:
        if backend_path in settings.AUTHENTICATION_BACKENDS:
            backend = load_backend(backend_path)
            user = backend.get_user(user_id)
            # Verify the session
            if hasattr(user, 'get_session_auth_hash'):
                session_hash = request.session.get(HASH_SESSION_KEY)
                session_hash_verified = session_hash and constant_time_compare(
                    session_hash,
                    user.get_session_auth_hash()
                )
                if not session_hash_verified:
                    request.session.flush()
                    user = None

    return user or AnonymousUser()

# def logout(request):
#     """
#     Removes the authenticated user's ID from the request and flushes their
#     session data.
#     """
#     # Dispatch the signal before the user is logged out so the receivers have a
#     # chance to find out *who* logged out.
#     user = getattr(request, 'user', None)
#     if hasattr(user, 'is_authenticated') and not user.is_authenticated:
#         user = None
#     user_logged_out.send(sender=user.__class__, request=request, user=user)
#
#     # remember language choice saved to session
#     language = request.session.get(LANGUAGE_SESSION_KEY)
#
#     request.session.flush()
#
#     if language is not None:
#         request.session[LANGUAGE_SESSION_KEY] = language
#
#     if hasattr(request, 'user'):
#         from django.contrib.auth.models import AnonymousUser
#         request.user = AnonymousUser()

############################################################
############################################################
