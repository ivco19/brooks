from django.urls import path

from reporter import views


urlpatterns = [
    path(
        'configuration/',
        views.ReportConfigurationView.as_view(),
        name='configuration')]
