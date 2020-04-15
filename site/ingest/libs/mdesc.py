import copy
import os
import json
import inspect

import yaml

from django.db import models, transaction
from django.core import validators
from django.contrib import admin

import numpy as np

import pandas as pd

import attr


# =============================================================================
# DOCS
# =============================================================================

"""Some insights about the code:
   https://dynamic-models.readthedocs.io/

"""


# =============================================================================
# USERFUL CLASSES
# =============================================================================

class MultiKeyDict(dict):
    def __init__(self, data):
        for keys, v in data.items():
            for k in keys:
                if k in self:
                    raise KeyError(
                        f"Duplicated key '{k}' for value {v} and {self[k]}")
                self[k] = v


class Bunch(dict):
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
    pass


class IncorrectConfigurationError(ValueError):
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


FIELD_TYPES = {
    "int": models.IntegerField,
    "float": models.FloatField,
    "date": models.DateField,
    "bool": models.BooleanField,
    "char": models.CharField,
    "freetext": models.TextField,
}


DATA_TRANSLATIONS = MultiKeyDict({
    # MODEL
    ("attributes", "atributos"): "attributes",
    ("meta", "Meta"): "meta",

    # META AND DMETA
    ("verbose_name_plural", "plural"): "verbose_name_plural",
    ("principal",): "principal",

    # field types
    ("int", "integer", "entero"): "int",
    ("float", "decimal", "flotante"): "float",
    ("date", "fecha"): "date",
    ("bool", "boolean", "booleano"): "bool",
    ("char", "text", "texto"): "char",
    ("freetext", "free", "libre", "textolibre"): "freetext",

    # FIELD_ATTRS
    ("type", "tipo"): "type",
    ("sep",): "sep",
    ("formato", "format"): "format",
    ("link", "enlace"): "link",

    ("length", "max_length", "largo"): "max_length",
    ("default",): "default",
    ("unique", "unico", "único"): "unique",
    ("opciones", "choices"): "choices",
    ("min",): "min",
    ("max",): "max",
    ("null", "vacio"): "null",

    ("related_name", "relacion", "relación"): "related_name",

    # FIELD_VALUES
    ("True", "true", "si", "Sí", "Si", "SI", "SÍ"): True,
    ("False", "false", "no", "No", "NO"): False,

})


NO_TRANSLATE = ["choices", "related_name"]


KEYS_TO_REMOVE = ["format", "tag", "link"]

ATTRS_DEFAULT = {
    "null": True
}


DMETA_ATTRS = {
    "principal": False
}

PLACEHOLDERS = {
    "date": "DD-MM-YYYY",
    "int": "1",
    "float": "1.2",
    "date": "DD-MM-YYYY",
    "bool": "true",
    "char": "str",
    "freetext": "str",
}


# =============================================================================
# FUNCTIONS
# =============================================================================

class Compiler:

    def translate(self, data):
        """Traduce todo lo que tiene el diccionario de datos
        si la llave traducida esta incluida en NO_TRANSLATE.

        """
        if isinstance(data, list):
            return [self.translate(e) for e in data]
        elif isinstance(data, dict):
            tdict = {}
            for k, v in data.items():
                tk = self.translate(k)
                tv = v if tk in NO_TRANSLATE else self.translate(v)
                tdict[tk] = tv
            return tdict
        return DATA_TRANSLATIONS.get(data, data)

    def create_field(self, *, name, data, emodels):
        # copiamos los datos para manipular tranquilos
        data = copy.deepcopy(data)

        # primero sacamos el tipo
        ftype = data.pop("type")
        dj_ftype = FIELD_TYPES.get(ftype, ftype)

        # aca saco todos las configuraciones que se usaran vara parsear y no
        # para crear cosas
        for tr in KEYS_TO_REMOVE:
            data.pop(tr, None)

        # add the default fields if not present
        for k, v in ATTRS_DEFAULT.items():
            if k not in data:
                data[k] = v

        # ahora el tipo puede ser uno nativo o un foreign key
        if inspect.isclass(dj_ftype) and issubclass(dj_ftype, models.Field):

            if "choices" in data:
                data["choices"] = [(e, e) for e in data["choices"]]

            fvalidators = []
            if "min" in data:
                min_value = data.pop("min")
                fvalidators.append(validators.MinValueValidator(min_value))
            if "max" in data:
                max_value = data.pop("max")
                fvalidators.append(validators.MaxValueValidator(max_value))
            if fvalidators:
                data["validators"] = fvalidators

            return dj_ftype(**data)

        else:
            # here we have some kind of FK
            link_to = emodels[dj_ftype]

            # if we have sep is a many to many
            sep = data.pop("sep", None)
            if sep:
                data.pop("null", None)
                return models.ManyToManyField(link_to, **data)
            else:
                return models.ForeignKey(
                    link_to, on_delete=models.CASCADE, **data)

    def create_model(self, *, name, data, emodels, module_spec):

        from django_extensions.db.models import TimeStampedModel as basemodel

        # copiamos los datos para manipular tranquilos
        original_data = copy.deepcopy(data)
        data = copy.deepcopy(data)

        # creamos el contenedor de todos los atributos para el modelo
        attrs = {'__module__': module_spec.name}

        # iteramos sobre
        attributes = data.pop("attributes", {})
        field_names = []
        for field_name, field_data in attributes.items():
            new_field = self.create_field(
                name=field_name, data=field_data, emodels=emodels)
            attrs[field_name] = new_field
            field_names.append(field_name)

        # sacamos los meta
        meta_attrs = data.pop("meta", {})

        # aca sacamos todo lo meta que es exclusivo de esta app
        dmeta_attrs = {
            dma: meta_attrs.pop(dma, default)
            for dma, default in DMETA_ATTRS.items()}
        dmeta_attrs["desc_name"] = name
        dmeta_attrs["field_names"] = tuple(field_names)
        dmeta_attrs["desc"] = original_data
        attrs["DMeta"] = type("DMeta", (object,), dmeta_attrs)

        # creamos la django Meta
        attrs["Meta"] = type("Meta", (object,), meta_attrs)

        # creamos el modelo en si
        modelcls = type(name, (basemodel,), attrs)

        return modelcls

    def mcompile(self, data, app_config):

        # sacamos el contexto del app.models
        context = vars(app_config.models_module)

        # sacamos todos los modelos preexistentes en el contexto
        emodels = {
            k: v for k, v in context.items()
            if inspect.isclass(v) and issubclass(v, models.Model)}
        dmodels = {}

        # buscamos en que modelo nos estan definiendo
        module_spec = context["__spec__"]

        # aca vamos a guardar el modelo dinamico principal que tiene que ser
        # ser uno y tiene que ser uno
        principal = None

        # creamos los nuevos modelos y los vamos agregando al contexto de
        # emodels pero ademas los separamos en su propio diccionario dmodels
        for model_name, model_data in data.items():

            # traducimos las llaves del dicionario de datos
            tmodel_data = self.translate(model_data)

            new_model = self.create_model(
                name=model_name, data=tmodel_data,
                emodels=emodels, module_spec=module_spec)

            # here we orchestrate if the model is the principal one
            if new_model.DMeta.principal and principal:
                raise ValueError(
                    "Duplicate principal model "
                    f"'{principal.__name__}' and '{new_model.__name__}'")
            elif new_model.DMeta.principal:
                principal = new_model

            dmodels[model_name] = new_model
            emodels[model_name] = new_model

        # if we process all the models and no one is principal
        # we have a problem
        if not principal:
            raise IncorrectConfigurationError("No principal model")

        # create a link inverted between name and model
        fields_to_model = MultiKeyDict({
            model.DMeta.field_names: model
            for model in dmodels.values()})

        # retornamos los nuevos modelos
        return Bunch(
            models=dmodels, principal=principal,
            fields_to_model=fields_to_model)


# =============================================================================
# ADMIN REGISTER
# =============================================================================

class AdminRegister:

    def register(self, models):
        regs = []
        for model_name, model in models.items():
            reg = admin.site.register(model, admin.ModelAdmin)
            regs.append(reg)
        return regs


# =============================================================================
# FILE_PARSER
# =============================================================================

class FileParser:

    def parse(self, df, models, principal, fields_to_model):
        merge_info = Bunch(info=[], warning=[], error=[])
        for row_idx, row in df.iterrows():
            prefix = f"Fila.{row_idx+1}"

            if np.all(row.isnull().values):
                merge_info.warning.append(f"{prefix} vacia")
                continue

            import ipdb; ipdb.set_trace()

            ipdb.set_trace()

        return Bunch(merge_info=merge_info, models=models)


# =============================================================================
# API
# =============================================================================

@attr.s(frozen=True, repr=False)
class DynamicModels:

    descfile = attr.ib()
    cache = attr.ib(init=False, factory=Bunch)
    compiler = attr.ib(init=False, factory=Compiler)
    admin = attr.ib(init=False, factory=AdminRegister)
    fileparser = attr.ib(init=False, factory=FileParser)

    def load_descriptor_file(self, filename):
        """Load the descfile based on the file extension"""
        ext = os.path.splitext(filename)[-1].lower()
        parser = DESCRIPTOR_FILE_PARSERS[ext]
        with open(filename) as fp:
            return parser(fp)

    def load_data_file(self, filename):
        """Load the data based on the file extension"""
        ext = os.path.splitext(filename)[-1].lower()
        parser = DATA_FILE_PARSERS[ext]
        return parser(filename)

    def create_models(self, app_config):
        if self.cache.get("compiled"):
            module_spec = self.models_context["__spec__"]
            raise MethodsCallOrderError(
                f"models already defined in {module_spec.name}")

        data = self.load_descriptor_file(self.descfile)
        compile_info = self.compiler.mcompile(data, app_config)

        self.cache.descfile_content = data
        self.cache.compiled = True
        self.cache.app_config = app_config
        self.cache.update(compile_info)

        # inject models into the context
        context = vars(app_config.models_module)
        context.update(compile_info.models)

    def register_admin(self, exclude=None):
        if not self.cache.compiled:
            raise MethodsCallOrderError("models not yet defined")

        exclude = [] if exclude is None else exclude
        models = {
            name: model
            for name, model in self.cache.models.items()
            if name not in exclude}
        return self.admin.register(models)

    def make_empty_df(self):
        principal = self.cache.principal
        fields_to_model = self.cache.fields_to_model
        desc = self.cache.descfile_content

        def extract_fields(model):
            dmodels = self.cache.models

            columns = []
            for fn in model.DMeta.field_names:
                mf = fields_to_model[fn]
                model_desc = mf.DMeta.desc

                attr_desc = model_desc["attributes"][fn]
                atype = attr_desc["type"]
                if atype in FIELD_TYPES:
                    columns.append((fn, PLACEHOLDERS[atype]))
                elif atype in dmodels:
                    amodel = dmodels[atype]
                    columns.extend(extract_fields(amodel))
            return columns

        row = extract_fields(principal)
        return pd.DataFrame([dict(row)])

    def merge_info(self, filepath):
        if not self.cache.compiled:
            raise MethodsCallOrderError("models not yet defined")

        df = self.load_data_file(filepath)

        with transaction.atomic():
            merge_info = self.fileparser.parse(
                df=df, models=self.cache.models,
                principal=self.cache.principal,
                fields_to_model=self.cache.fields_to_model)

            # make the rollback
            transaction.set_rollback(True)
        raise Exception()
        return merge_info
