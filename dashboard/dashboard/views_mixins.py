from django.contrib.messages.views import SuccessMessageMixin


class LogginRequired(UserPassesTestMixin):

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_active