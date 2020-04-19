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

from django.core.checks import Error, register
from django.apps import apps

from ingest.models import BaseIngestModel

# =============================================================================
# CONSTANTS
# =============================================================================

app = apps.get_app_config("ingest")


# =============================================================================
# FUNCTIONS
# =============================================================================

@register()
def one_principal_check(app_configs, **kwargs):
    """Check if we have only one principal in all the ingest models"""
    errors = []
    principals = [
        m for m in app.get_models()
        if issubclass(m, BaseIngestModel) and m.principal]
    if len(principals) != 1:
        msg = (
            "Only one principal models is allowed. "
            f"found {len(principals)}: {principals}")
        errors.append(
            Error(
                msg, hint=f"Put some principals to false in ingest.models",
                id="ingest.E001"))
    return errors


@register()
def identifiers_check(app_configs, **kwargs):
    errors = []
    for m in app.get_models():
        if not issubclass(m, BaseIngestModel):
            continue
        mname = m.model_name()
        if m.identifier is None:
            errors.append(
                Error(f"Model {mname} need a identifier field"))
        if not hasattr(m, m.identifier):
            errors.append(
                Error(
                    f"Field identifier '{m.identifier}' not found "
                    f"in model {mname}"))

        field = getattr(m, m.identifier).field
        if field.null or not field.unique:
            errors.append(
                Error(
                    f"Field identifier '{mname}.{m.identifier}' "
                    "must be unique and not null"))

    return errors
