#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Arcovid-19 Brooks.
# Copyright (c) 2020, Juan B Cabral, Vanessa Daza, Diego García Lambas,
#                     Marcelo Lares, Nadia Luczywo, Dante Paz, Rodrigo Quiroga,
#                     Bruno Sanchez, Federico Stasyszyn.
# License: BSD-3-Clause
#   Full Text: https://github.com/ivco19/brooks/blob/master/LICENSE


# =============================================================================
# DOCS
# =============================================================================

"""Signals for the ingest models."""


# =============================================================================
# IMPORTS
# =============================================================================


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

from ingest import models


# =============================================================================
# CONSTANTS
# =============================================================================

app = apps.get_app_config("ingest")


# =============================================================================
# SIGNALS
# =============================================================================

@receiver(post_save, sender=models.RawFile)
def compile_file(sender, instance, created, **kwargs):
    """Check if a raw file must be merged or deleted from the database.

    """
    if created:
        try:
            instance.size = len(instance.as_df())
        except Exception:
            instance.broken = True

    if instance.broken:
        return
    elif instance.merged and not instance.is_parsed:
        app.ingestor.merge(
            user=instance.modify_by, raw_file=instance)
    elif not instance.merged and instance.is_parsed:
        app.ingestor.unmerge(raw_file=instance)
