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
        'list_dmodel/<dmodel>/',
        views.ListDmodelView.as_view(),
        name='list_dmodel'),

    path(
        'plot_dmodel/<dmodel>/',
        views.PlotDmodelView.as_view(),
        name='plot_dmodel'),

    # path(
    #     'patient/<int:pk>/',
    #     views.PatientDetailView.as_view(),
    #     name='patient_detail')
]
