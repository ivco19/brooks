import copy
import os
import json
import inspect
import datetime as dt
import traceback

import yaml

from django.db import models, transaction
from django.core import validators
from django.contrib import admin
from django.db.utils import IntegrityError
from django.db.transaction import TransactionManagementError

import dateutil.parser

import numpy as np

import pandas as pd

import attr


# =============================================================================
# DOCS
# =============================================================================

"""First wellcome to the thunderdome-bitch, this module Understand, parses
nformation from a spreadsheet


"""


# =============================================================================
# USERFUL CLASSES
# =============================================================================

class Bunch(dict):
    """A dict but a "." attribute accesor (mostly copyed from sklearn)."""
    def __getattr__(self, a):
        return self[a]

    def __dir__(self):
        return super().__dir__() + list(self.keys())

    def __repr__(self):
        return f"Bunch({', '.join(self.keys())})"

    def __setattr__(self, a, v):
        self[a] = v


class MergeInfo(dict):
    """To simplfy the code inside the file parser"""

    def __init__(self):
        self.active_row = 0
        self.update(info=[], warning=[], error=[])

    def _write(self, level, msg):
        self[level].append(f"[F.{self.active_row}] {msg}")

    def info(self, msg):
        self._write("info", msg)

    def warning(self, msg):
        self._write("warning", msg)

    def error(self, msg):
        self._write("error", msg)


# =============================================================================
# ERROR
# =============================================================================

class ParseError(RuntimeError):
    """We can't parse the spreadsheet with data"""
    pass


# =============================================================================
# CONSTANTS
# =============================================================================

LINK_TYPES = (models.ManyToManyField, models.ForeignKey)

PLACEHOLDERS = {
    models.IntegerField: "0",
    models.FloatField: "0.0",
    models.DateField: "DD-MM-YY",
    models.BooleanField: "si/no",
    models.CharField: "texto",
    models.TextField: "texto libre"
}


def parse_date(x):
    try:
        return x.date()
    except Exception as err:
        return dateutil.parser.parse(x).date()


def no_parser(x):
    return x


FIELD_PARSERS = {
    models.IntegerField: int,
    models.FloatField: float,
    models.DateField: parse_date,
    models.BooleanField: lambda x: (str(x).lower() in "yes on si true 1"),
    models.CharField: str,
    models.TextField: str
}


FORBIDDEN_NAMES = (
    "user", "created_by", "modified_by", "created", "modified", "id",
    "password", "secret", "loggin", "superuser", "staff", "login", "raw_file")


# =============================================================================
# FUNCTIONS
# =============================================================================

def is_name_forbidden(fname):
    fname = fname.lower()
    if fname.startswith("_"):
        return True
    for forbidden in FORBIDDEN_NAMES:
        if forbidden in fname.split("_"):
            return True
    return False


# =============================================================================
# API
# =============================================================================

@attr.s(frozen=True, repr=False)
class Ingestor:
    """The public api here. This class must be instantiated in the
    AppConfig and then you must call first the create_models method in the
    ready method.

    """
    app = attr.ib()

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def get_principal(self):
        for m in self.get_ingest_models():
            if m.principal:
                return m

    def get_ingest_models(self):
        BaseIngestModel = self.app.models_module.BaseIngestModel

        def dmodels_key(m):
            if m.principal:
                return ""
            return m.model_name()

        dmodels = [
            m for m in self.app.get_models()
            if issubclass(m, BaseIngestModel)]
        dmodels.sort(key=dmodels_key)

        return dmodels

    def get_model(self, model_name):
        for model in self.get_ingest_models():
            if model_name == model.model_name():
                return model

    # =========================================================================
    # EMPTY SPREADSHEET
    # =========================================================================

    def make_empty_df(self):
        dmodels = self.get_ingest_models()
        principal = self.get_principal()

        def extract_fields(model):
            if model not in dmodels:
                return []

            fields = {
                fn: ft for fn, ft in model.get_fields().items()
                if fn not in FORBIDDEN_NAMES}
            if model.principal:
                fields.pop(model.identifier, None)

            columns = []
            for fn, ft in fields.items():
                if not isinstance(ft, LINK_TYPES):
                    ph = PLACEHOLDERS.get(type(ft), "")
                    columns.append((fn, ph))
                else:
                    rmodel = ft.related_model
                    columns.extend(extract_fields(rmodel))
            return columns

        row = extract_fields(principal)
        return pd.DataFrame([dict(row)])

    # =========================================================================
    # INSTANTIATION
    # =========================================================================

    def _parse(self, user, raw_file):
        me = MergeInfo()

        df = raw_file.as_df()

        # remove nan for None
        df = df.where(pd.notnull(df), None)

        # retrieve all the dmodels
        dmodels = self.get_ingest_models()
        principal = self.get_principal()

        # internal func
        def split_for_model(model, rdata):
            field_names = [
                fn for fn in model.get_fields().keys()
                if fn not in FORBIDDEN_NAMES]

            no_model_data = {
                k: v for k, v in rdata.items() if k not in field_names}

            model_data = {}
            for k in field_names:
                v = rdata.get(k)
                if v is not None:
                    v = str(v).split(";")
                else:
                    if model.identifier == k:
                        model_name = model.model_name()
                        raise ParseError(
                            f"No se puede crear un {model_name} con "
                            f"{model.identifier} vacio")
                    v = []
                model_data[k] = v

            max_split = max(map(len, model_data.values()))

            datas = []
            for idx in range(max_split):
                d = {}
                for k, v in model_data.items():
                    d[k] = v[idx] if idx < len(v) else None
                d.update(no_model_data)
                datas.append(d)
            return datas

        def create_instance(model, rdata):
            rdata = rdata.copy()

            # parseamos todos los atributos y los dividimos en
            # tipos nativos, fks, y m2ms
            n_fields, fk_fields, m2m_fields = {}, {}, {}
            for fn, ft in model.get_fields().items():
                if fn in FORBIDDEN_NAMES:
                    continue
                if isinstance(ft, models.ForeignKey):
                    fk_fields[fn] = ft.related_model
                elif isinstance(ft, models.ManyToManyField):
                    m2m_fields[fn] = ft.related_model
                else:
                    rvalue = rdata.pop(fn, None)
                    if rvalue is not None:
                        parser = FIELD_PARSERS.get(type(ft), no_parser)
                        n_fields[fn] = parser(rvalue)

            # creamos o modificamos la instancia en cuestion
            if model.principal:
                instance = model(
                    raw_file=raw_file,
                    created_by=user, modified_by=user, **n_fields)
            else:
                model_name = model.model_name()
                identifier_value = n_fields.get(model.identifier)
                if identifier_value is None:
                    raise ParseError(
                        f"No se puede crear un {model_name} con "
                        f"{model.identifier} vacio")

                query = {model.identifier: identifier_value}
                qs = model.objects.filter(**query)
                create = not qs.exists()

                if create:
                    me.info(f"Nuevo {model_name} '{query}'")
                    instance = model(
                        created_by=user, modified_by=user, **n_fields)

                else:
                    instance = qs.first()
                    instance.modified_by = user
                    preffix = (
                        f"Se mofica en {model_name} '{query}' el atributo")
                    for k, v in n_fields.items():
                        actual = getattr(instance, k)
                        if actual != v:
                            me.warning(f"{preffix}_'{k}': {actual} --> {v}")
                        setattr(k, v)

            # creamos el los fks
            fk_instances = Bunch()
            for k, v in fk_fields.items():
                fk_instances[k] = create_instance(v, rdata)

            # creamos los m2m
            m2m_instances = Bunch()
            for k, v in m2m_fields.items():
                m2minsts = []
                for sdata in split_for_model(v, rdata):
                    m2minsts.append(create_instance(v, sdata))
                m2m_instances[k] = m2minsts

            return Bunch({
                "instance": instance,
                "fk": fk_instances,
                "m2m": m2m_instances})

        # END INTERNAL FUNC
        instances = []
        for idx, row in df.iterrows():
            rdata = row.to_dict()
            me.active_row = idx + 1
            try:
                rinstances = create_instance(principal, rdata)
            except ParseError as err:
                me.error(str(err))
            instances.append(rinstances)

        return instances, dict(me)

    def merge_info(self, user, raw_file):
        _, me = self._parse(user, raw_file)
        return me

    def remove(self, raw_file):
        raise NotImplementedError()
        if not self.cache.compiled:
            raise MethodsCallOrderError("models not yet defined")
        with transaction.atomic():
            merge_info = self.fileparser.remove(
                raw_file=raw_file)
        return merge_info
