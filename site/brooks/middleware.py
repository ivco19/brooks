#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Arcovid-19 Brooks.
# Copyright (c) 2020, Juan B Cabral, Vanessa Daza, Diego García Lambas,
#                     Marcelo Lares, Nadia Luczywo, Dante Paz, Rodrigo Quiroga,
#                     Bruno Sanchez, Federico Stasyszyn.
# License: BSD-3-Clause
#   Full Text: https://github.com/ivco19/brooks/blob/master/LICENSE


# =============================================================================
# IMPORTS
# =============================================================================

from django.contrib.auth.models import User
from django.conf import settings

from django.contrib.auth import authenticate

from django.utils.deprecation import MiddlewareMixin


# =============================================================================
# CLASSES
# =============================================================================

class DemoUserMiddleware(MiddlewareMixin):
    """Automatically creates and login a user for the demo mode"""

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
