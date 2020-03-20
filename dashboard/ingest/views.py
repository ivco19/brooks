from django.shortcuts import render

# Create your views here.
from django.urls import path

from . import views

from django.contrib.auth import views as auth_views


urlpatterns = [
    # path('login/', auth_views.LoginView.as_view()),
    # path('logout/', auth_views.LogoutView.as_view(), name="logout"),


    # =========================================================================
    # DASHBOARD
    # =========================================================================

    path('', ChangesView.as_view(), name="dashboard"),

    # =========================================================================
    # MISC
    # =========================================================================

    path(
        'changes/',
        views.ChangesView.as_view(),
        name='changes')


]
