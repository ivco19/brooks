from django.urls import path

from webtools import views


urlpatterns = [
    path(
        'show/<tool>/',
        views.ShowView.as_view(),
        name='show')]
