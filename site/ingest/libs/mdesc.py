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

"""First wellcome to the thunderdome-bitch, this module understand, parses
and compile the model-description file (model.yml/model.json) files.

This code is clean but complex. Its use a lot of:

- Django internals.
- Python meta-programming.
- Recursion.

This module is fun but take care heare.

Some insights about the code:
   https://dynamic-models.readthedocs.io/

"""


# =============================================================================
# USERFUL CLASSES
# =============================================================================

class MultiKeyDict(dict):
    """Receives another dictionay as a contructor, and split the keys
    internally. Also explodes if a key es repeated.

    """
    def __init__(self, data):
        for keys, v in data.items():
            for k in keys:
                if k in self:
                    raise KeyError(
                        f"Duplicated key '{k}' for value {v} and {self[k]}")
                self[k] = v


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


# =============================================================================
# ERROR
# =============================================================================

class MethodsCallOrderError(RuntimeError):
    """You call the methods in the wrong order."""
    pass


class IncorrectConfigurationError(ValueError):
    """The model.yml/json file is bad defined."""
    pass


class ParseError(RuntimeError):
    """We can't parse the spreadsheet with data"""
    pass


# =============================================================================
# CONSTANTS
# =============================================================================

DESCRIPTOR_FILE_PARSERS = MultiKeyDict({
    (".yaml", ".yml"): yaml.safe_load,
    (".json",): json.load,
})


DATA_FILE_PARSERS = MultiKeyDict({
    (".csv",): pd.read_csv,
    (".xlsx",): pd.read_excel,
})


DATA_FILE_EXTENSIONS = list(DATA_FILE_PARSERS)





class FIELD_PARSERS:

    def __getitem__(self, ftype):
        key = f"parse_{ftype}"
        return getattr(self, key, self.no_parse)

    def no_parse(self, x, **kwargs):
        return x

    def parse_int(self, x, **kwargs):
        return int(x)

    def parse_float(self, x, **kwargs):
        return float(x)

    def parse_date(self, x, **kwargs):
        if isinstance(x, pd.Timestamp):
            return x.date()
        format = kwargs.get("format")
        if format:
            return dt.datetime.strfparse(x, format).date()
        return dateutil.parser.parse(x).date()

    def parse_bool(self, x, **kwargs):
        return bool(x)

    def parse_char(self, x, **kwargs):
        return str(x)

    def parse_freetext(self, x, **kwargs):
        return str(x)


FIELD_PARSERS = FIELD_PARSERS()


FORBIDDEN_NAMES = (
    "user", "created_by", "modified_by", "created", "modified", "id",
    "password", "secret", "loggin", "superuser", "staff", "login")


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
# FILE_PARSER
# =============================================================================

class FileParser:
    """Validate the data-spreadsheet with the description file and
    created model-instances of their values.

    """

    def make_minfo(self):
        return Bunch(info=[], warning=[], error=[])

    def merge_minfo(self, a, b, prefix=None):
        merged = Bunch(copy.deepcopy(dict(a)))
        for k, v in merged.items():
            for msg in b[k]:
                if prefix:
                    v.append(f"{prefix} {msg}")
                else:
                    v.append(msg)
        return merged

    def get_or_create(self, *, model, query, cache, defaults):
        # esta porqueria es un workarround para no hacer queries en una
        # transaccion
        mcache = cache[model]
        for e in mcache:
            ed = {qk: getattr(e, qk) for qk in query}
            if ed == query:
                return e, False

        full_data = query.copy()
        full_data.update(defaults)
        inst = model(**full_data)
        mcache.append(inst)
        return inst, True

    def m2m_split_data(self, model, sep, data):
        field_names = model.DMeta.field_names
        no_model_data = {k: v for k, v in data.items() if k not in field_names}
        model_data = {k: str(data.get(k, "")).split(sep) for k in field_names}
        max_split = max(map(len, model_data.values()))

        datas = []
        for idx in range(max_split):
            d = {}
            for k, v in model_data.items():
                d[k] = v[idx] if idx < len(v) else None
            d.update(no_model_data)
            datas.append(d)
        return datas

    def diff_instance(self, instance, s_data):
        for k, v in s_data.items():
            odata = getattr(instance, k)
            if v is not None and odata != v:
                yield k, v

    def create_model_instance(
        self, *, cache, model, data, models,
        is_principal, created_by, raw_file,
    ):
        mm_info = self.make_minfo()
        model_name = model.DMeta.desc_name
        model_desc = model.DMeta.desc
        fields_names = model.DMeta.field_names
        identifier = model.DMeta.identifier

        # sacamos los datos en crudo
        model_data = {k: data.get(k) for k in fields_names}

        # ahora parseamos todo lo que no sea foreignkey
        s_data, m2m_data = {}, {}
        for fname, fvalue in model_data.items():

            field_desc = model_desc["attributes"][fname]
            field_type = field_desc["type"]

            if field_type in FIELD_TYPES:
                # es nativo
                try:
                    fvalue = (
                        None if fvalue is None else
                        FIELD_PARSERS[field_type](fvalue, **field_desc))
                except Exception as err:
                    raise ParseError(str(err))

                s_data[fname] = fvalue
            elif field_type in models:

                # hay que orquestar el tema de los foreign key
                sep = field_desc.get("sep")

                if sep:  # M2;
                    rel_model = models[field_type]
                    m2m_splited_data = self.m2m_split_data(
                        rel_model, sep, data)
                    m2m_instances = []
                    for m2md in m2m_splited_data:
                        rel_mminfo, rel_instance = self.create_model_instance(
                            model=rel_model, data=m2md, created_by=created_by,
                            raw_file=raw_file, models=models, cache=cache,
                            is_principal=False)
                        m2m_instances.append(rel_instance)
                        mm_info = self.merge_minfo(mm_info, rel_mminfo)
                    m2m_data[fname] = m2m_instances
                else:  # FK
                    rel_model = models[field_type]
                    rel_mminfo, rel_instance = self.create_model_instance(
                        model=rel_model, data=data, created_by=created_by,
                        raw_file=raw_file, models=models,
                        is_principal=False, cache=cache)
                    s_data[fname] = rel_instance
                    mm_info = self.merge_minfo(mm_info, rel_mminfo)

        identf_value = s_data[identifier]
        query = {identifier: identf_value}

        # si se crea uno nuevo se crea con esto
        defaults = {"created_by": created_by, "modified_by": created_by}
        if is_principal:
            defaults.update(raw_file=raw_file)

        instance, created = self.get_or_create(
            model=model, defaults=defaults, query=query, cache=cache)

        if created:
            for k, v in s_data.items():
                setattr(instance, k, v)

            if not is_principal:
                mm_info.info.append(
                    f"Nuevo {model_name} con {identifier}={identf_value}")
        else:
            if is_principal:
                raise ParseError(
                    f"{model_name} con {identifier}={identf_value} duplicado")
            for k, v in self.diff_instance(instance, s_data):
                setattr(instance, k, v)
                mm_info.warning.append(
                    f"Cambio valor de {model_name} con "
                    f"{identifier}={identf_value} en el valor de {k}")

        try:
            instance.save()
        except IntegrityError as err:
            raise ParseError(
                f"Los datos rompen el esquema con respecto a "
                f"cargas anteriores ({str(err)})")
            return mm_info, instance

        for k, links in m2m_data.items():
            manager = getattr(instance, k)
            for v in links:
                try:
                    manager.add(v)
                except Exception as err:
                    mm_info.error.append(str(err))
                    return mm_info, instance

        return mm_info, instance

    def parse(
        self, *, df, models, principal, rollback,
        fields_to_model, created_by, raw_file
    ):
        merge_info = self.make_minfo()
        new_instances = []

        cache = {
            m: list(m.objects.all())
            for m in models.values()}
        with transaction.atomic():
            # try:
            new_instances = []
            for row_idx, row in df.iterrows():
                prefix = f"[Fila.{row_idx+1}]"

                if np.all(row.isnull().values):
                    merge_info.warning.append(f"{prefix} vacia")
                    continue

                data = row.where(pd.notnull(row), None).to_dict()
                try:
                    mminfo, instance = self.create_model_instance(
                        cache=cache, model=principal, data=data,
                        created_by=created_by, raw_file=raw_file,
                        models=models, is_principal=True)
                    new_instances.append(instance)
                except ParseError as err:
                    merge_info.warning.append(f"{prefix} {str(err)}")
                else:
                    merge_info = self.merge_minfo(
                        merge_info, mminfo, prefix=prefix)
            # except Exception as err:
            #     merge_info.error.append(
            #         "Algo no salió como lo planeábamos,"
            #         "por favor envia este mensaje junto con el archivo que lo"
            #         "generó a los desarrolladores. \n\n"
            #         f"{traceback.format_exc()}")
            if rollback:
                transaction.set_rollback(True)

        return Bunch(
            merge_info=merge_info, new_instances=new_instances, df=df)

    def remove(self, raw_file):
        return raw_file.generated.all().delete()


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
    fileparser = attr.ib(init=False, factory=FileParser)

    # =========================================================================
    # FILE PARSERS
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

    def make_empty_df(self):
        placeholders = {
            models.IntegerField: "0",
            models.FloatField: "0.0",
            models.DateField: "DD-MM-YY",
            models.BooleanField: "si/no",
            models.CharField: "texto",
            models.TextField: "texto libre"
        }

        link_types = (models.ManyToManyField, models.ForeignKey)

        dmodels = self.get_ingest_models()
        principal = self.get_principal()

        def extract_fields(model):
            print(model, "<<<<")
            if model not in dmodels:
                return []

            fields = {
                fn: ft for fn, ft in model.get_fields().items()
                if fn not in FORBIDDEN_NAMES}
            if model.principal:
                fields.pop(model.identifier, None)

            columns = []
            for fn, ft in fields.items():
                if not isinstance(ft, link_types):
                    ph = placeholders.get(type(ft), "")
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

    def merge_info(self, created_by, raw_file):
        # if not self.cache.compiled:
        #    raise MethodsCallOrderError("models not yet defined")
        raise NotImplementedError()

        filepath = raw_file.file.path
        df = self.load_data_file(filepath)

        merge_info = self.fileparser.parse(
            created_by=created_by, raw_file=raw_file,
            df=df, models=self.cache.models, rollback=True,
            principal=self.cache.principal,
            fields_to_model=self.cache.fields_to_model)

        return merge_info

    def merge(self, created_by, raw_file):
        raise NotImplementedError()
        if not self.cache.compiled:
            raise MethodsCallOrderError("models not yet defined")

        filepath = raw_file.file.path
        df = self.load_data_file(filepath)

        merge_info = self.fileparser.parse(
            created_by=created_by, raw_file=raw_file,
            df=df, models=self.cache.models,
            principal=self.cache.principal, rollback=False,
            fields_to_model=self.cache.fields_to_model)

        return merge_info

    def remove(self, raw_file):
        raise NotImplementedError()
        if not self.cache.compiled:
            raise MethodsCallOrderError("models not yet defined")
        with transaction.atomic():
            merge_info = self.fileparser.remove(
                raw_file=raw_file)
        return merge_info
