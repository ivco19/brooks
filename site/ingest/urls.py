from django.urls import path

from ingest import views


urlpatterns = [
    path(
        'upload/',
        views.UploadRawFileView.as_view(),
        name='upload'),

    path(
        'chek_file/<int:pk>/',
        views.CheckRawFileView.as_view(),
        name='check_file')]
