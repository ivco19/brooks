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

from django.views.decorators.cache import cache_page

from django.contrib.auth.mixins import UserPassesTestMixin


# =============================================================================
# CLASSES
# =============================================================================

class LogginRequired(UserPassesTestMixin):
    """This mixin ensures that the user must be logged-in.

    This was copied from some recipe in the django-project page.

    """
    loggin_require_super_user = False
    loggin_require_staff = False

    def test_func(self):
        user = self.request.user
        staff = (
            (user.is_staff or user.is_superuser)
            if self.loggin_require_staff else True)
        super_user = (
            user.is_superuser
            if self.loggin_require_super_user else True)
        return (
            user.is_authenticated and user.is_active and staff and super_user)


class CacheMixin(object):
    # https://stackoverflow.com/a/26858638
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        timeout = self.get_cache_timeout()
        original_dispatch = super(CacheMixin, self).dispatch
        decorator = cache_page(timeout)
        cached_dispatch = decorator(original_dispatch)
        return cached_dispatch(*args, **kwargs)
