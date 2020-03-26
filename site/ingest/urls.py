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
        name='check_file'),

    path(
        'list_files/',
        views.ListRawFileView.as_view(),
        name='list_files'),

    path(
        'list_patient/',
        views.ListPatientView.as_view(),
        name='list_patient'),

    path(
        'patient/<int:pk>/',
        views.PatientDetailView.as_view(),
        name='patient_detail')]
