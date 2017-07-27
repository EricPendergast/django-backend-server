from django.conf import settings
from eledata import auth
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

# The authentication middleware needs to be reimplemented so that it works with
# mongoengine User objects. This allows for django automatic sessions. i.e.
# after you call 'eledata.auth.login', 'request.user' will be the user in the
# current session.

def get_user(request):
    if not hasattr(request, '_cached_user'):
        request._cached_user = auth.get_user(request)
    return request._cached_user


class CustomAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE%s setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")
        request.user = SimpleLazyObject(lambda: get_user(request))
