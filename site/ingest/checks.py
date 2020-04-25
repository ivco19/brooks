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

        if m.principal:
            if m.identifier is not None:
                msg = f"Identifier for principal Model {mname} is forbiden"
                hint = f"Remove the identifier attribute for model {mname}"
                errors.append(
                    Error(msg, hint=hint, id="ingest.E010"))
        else:

            if m.identifier is None:
                msg = f"Model {mname} need a identifier field"
                hint = (
                    f"Define the identifier class attribute in model {mname}")
                errors.append(
                    Error(msg, hint=hint, id="ingest.E011"))

            if not hasattr(m, m.identifier):
                msg = (
                    f"Field identifier '{m.identifier}' not found "
                    f"in model {mname}")
                hint = f"Define the field {m.identifier} in the model {mname}"
                errors.append(
                    Error(msg, hint=hit, id="ingest.E012"))

            field = getattr(m, m.identifier).field
            if field.null or not field.unique:
                msg = (
                    f"Field identifier '{mname}.{m.identifier}' "
                    "must be unique and not null")
                hint = (
                    "Remove the null attribute or add 'unique=True' "
                    f"to the field '{mname}.{m.identifier}'")
                errors.append(
                    Error(msg, hint=hint, id="ingest.E013"))

    return errors


@register()
def duplicated_ingest_fields_check(app_configs, **kwargs):
    # this fields can be duplicated if they are not the identifier
    allow_duplicated = [
        "id", "created", "modified", "created_by", "modified_by"]

    model_by_fields = {}

    errors = []
    for m in app.get_models():
        if not issubclass(m, BaseIngestModel):
            continue
        mname = m.model_name()
        identifier = m.identifier
        for fname in m.get_fields().keys():
            if fname in allow_duplicated and fname != identifier:
                continue
            elif fname in model_by_fields:
                msg = (
                    f"Duplicated field '{fname}' in models "
                    f"{mname} and {model_by_fields[fname]}")
                hint = f"Change the name of the field '{mname}.{fname}'"
                errors.append(
                    Error(msg, hint=hint, id="ingest.E020"))
            else:
                model_by_fields[fname] = mname
    return errors
