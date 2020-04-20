
from django.contrib.auth.models import User
from django.conf import settings

from django.contrib.auth import authenticate

from django.utils.deprecation import MiddlewareMixin


class DemoUserMiddleware(MiddlewareMixin):

    def process_request(self, request):
        assert hasattr(request, 'user'), "The Login Required Middleware"

        if not settings.DEMO_MODE:
            return

        user = request.user
        if user is None or not user.is_authenticated:
            user, _ = User.objects.get_or_create(
                username="demo",
                first_name="Demoscletes",
                last_name="Cledemo",
                email="demo@brooks.com",
            )
            user.set_password("")

            authenticate(username="demo", password='')
            request.user = user



