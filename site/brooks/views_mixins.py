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

from django.contrib.auth.mixins import UserPassesTestMixin


# =============================================================================
# CLASSES
# =============================================================================

class LogginRequired(UserPassesTestMixin):
    """This mixin ensures that the user must be logged-in.

    This was copied from some recipe in the django-project page.

    """

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_active
