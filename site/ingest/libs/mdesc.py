import copy
import os
import json
import inspect
import datetime as dt

import yaml

from django.db import models, transaction
from django.core import validators
from django.contrib import admin

import dateutil.parser

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


class ParseError(RuntimeError):
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

    ("format", "formato"): "format",
    ("tag", ): "tag",
    ("link", "enlace"): "link",
    ("identifier", "identificador"): "identifier",

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

KEYS_TO_REMOVE = ["format", "tag", "link", "identifier"]

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


FORBIDEN_FIELDS = ["user", "created_by", "created", "modified"]


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
        if name in FORBIDEN_FIELDS:
            raise IncorrectConfigurationError(
                f"El nombre de atributo {name} esta prohibido")

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

            if "sep" in data:
                raise IncorrectConfigurationError(
                    "sep solo puede ser definida con una referencia")

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

        basemodel = emodels["TimeStampedModel"]

        # copiamos los datos para manipular tranquilos
        original_data = copy.deepcopy(data)
        data = copy.deepcopy(data)

        # creamos el contenedor de todos los atributos para el modelo
        attrs = {'__module__': module_spec.name}

        # iteramos sobre
        attributes = data.pop("attributes", {})
        field_names, identifier = [], None
        for field_name, field_data in attributes.items():

            if "identifier" in field_data:
                if identifier:
                    raise IncorrectConfigurationError(
                        f"Model '{name}' has more than one identifier")
                elif field_data["type"] not in FIELD_TYPES:
                    raise IncorrectConfigurationError(
                        f"Model '{name}' identifier cant be a reference")

                identifier = field_name
                field_data["unique"] = True
                field_data["null"] = False

            new_field = self.create_field(
                name=field_name, data=field_data, emodels=emodels)
            attrs[field_name] = new_field
            field_names.append(field_name)

        if identifier is None:
            raise IncorrectConfigurationError(
                f"Missing identifier for Model '{name}'")

        # sacamos los meta
        meta_attrs = data.pop("meta", {})

        # aca sacamos todo lo meta que es exclusivo de esta app
        dmeta_attrs = {
            dma: meta_attrs.pop(dma, default)
            for dma, default in DMETA_ATTRS.items()}
        dmeta_attrs["desc_name"] = name
        dmeta_attrs["field_names"] = tuple(field_names)
        dmeta_attrs["desc"] = original_data
        dmeta_attrs["identifier"] = identifier
        dmeta_attrs["verbose_name_title"] = meta_attrs.get(
            "verbose_name_plural", name).title()
        attrs["DMeta"] = type("DMeta", (object,), dmeta_attrs)

        # si es el principal necesitamos linkerarlo a rawfile
        if dmeta_attrs["principal"]:
            attrs["raw_file"] = models.ForeignKey(
                emodels["RawFile"], on_delete=models.CASCADE,
                related_name="generated", verbose_name="Archivo")
            attrs["created_by"] = models.ForeignKey(
                emodels["User"], on_delete=models.CASCADE,
                related_name="generated", verbose_name="Creado por")

        # creamos un repr aceptable
        def __repr__(self):
            desc_name = self.DMeta.desc_name
            identifier = self.DMeta.identifier
            ivalue = getattr(self, identifier)
            return f"{desc_name}({identifier} => {ivalue})"

        attrs["__repr__"] = __repr__

        def __str__(self):
            desc_name = self.DMeta.desc_name
            identifier = self.DMeta.identifier
            ivalue = getattr(self, identifier)
            return ivalue

        attrs["__str__"] = __str__

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
        self, model, data, models, is_principal, created_by, raw_file,
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
                            raw_file=raw_file, models=models,
                            is_principal=False)
                        m2m_instances.append(rel_instance)
                        mm_info = self.merge_minfo(mm_info, rel_mminfo)
                    m2m_data[fname] = m2m_instances
                else:  # FK
                    rel_model = models[field_type]
                    rel_mminfo, rel_instance = self.create_model_instance(
                        model=rel_model, data=data, created_by=created_by,
                        raw_file=raw_file, models=models, is_principal=False)
                    s_data[fname] = rel_instance
                    mm_info = self.merge_minfo(mm_info, rel_mminfo)

        identf_value = s_data[identifier]
        query = {identifier: identf_value}
        if is_principal:
            query.update(created_by=created_by, raw_file=raw_file)

        instance, created = model.objects.get_or_create(**query)
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

        instance.save()
        for k, links in m2m_data.items():
            manager = getattr(instance, k)
            for v in links:
                manager.add(v)

        return mm_info, instance

    def parse(
        self, df, models, principal,
        fields_to_model, created_by, raw_file
    ):
        merge_info = self.make_minfo()
        new_instances = []
        for row_idx, row in df.iterrows():
            prefix = f"[Fila.{row_idx+1}]"

            if np.all(row.isnull().values):
                merge_info.warning.append(f"{prefix} vacia")
                continue

            data = row.where(pd.notnull(row), None).to_dict()
            try:
                mminfo, instance = self.create_model_instance(
                    model=principal, data=data, created_by=created_by,
                    raw_file=raw_file, models=models, is_principal=True)
                new_instances.append(instance)
            except ParseError as err:
                merge_info.warning.append(f"{prefix} {str(err)}")
            else:
                merge_info = self.merge_minfo(
                    merge_info, mminfo, prefix=prefix)

        return Bunch(
            merge_info=merge_info, new_instances=new_instances, df=df)

    def remove(self, raw_file):
        return raw_file.generated.all().delete()


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

    # =========================================================================
    # FILE PARSERS
    # =========================================================================

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

    # =========================================================================
    # MODELS CREATION
    # =========================================================================

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

    # =========================================================================
    # INSTANTIATION
    # =========================================================================

    def merge_info(self, created_by, raw_file):
        if not self.cache.compiled:
            raise MethodsCallOrderError("models not yet defined")

        filepath = raw_file.file.path
        df = self.load_data_file(filepath)

        with transaction.atomic():
            merge_info = self.fileparser.parse(
                created_by=created_by, raw_file=raw_file,
                df=df, models=self.cache.models,
                principal=self.cache.principal,
                fields_to_model=self.cache.fields_to_model)
            transaction.set_rollback(True)

        return merge_info

    def merge(self, created_by, raw_file):
        if not self.cache.compiled:
            raise MethodsCallOrderError("models not yet defined")

        filepath = raw_file.file.path
        df = self.load_data_file(filepath)

        with transaction.atomic():
            merge_info = self.fileparser.parse(
                created_by=created_by, raw_file=raw_file,
                df=df, models=self.cache.models,
                principal=self.cache.principal,
                fields_to_model=self.cache.fields_to_model)

        return merge_info

    def remove(self, raw_file):
        if not self.cache.compiled:
            raise MethodsCallOrderError("models not yet defined")
        with transaction.atomic():
            merge_info = self.fileparser.remove(
                raw_file=raw_file)

        return merge_info

    # =========================================================================
    # VIEWS HELPERS
    # =========================================================================

    def list_models(self):
        principal_vn = self.cache.principal._meta.verbose_name_plural.title()
        model_list = {
            principal_vn: self.cache.principal.DMeta.desc_name
        }
        for name, model in sorted(self.cache.models.items()):
            if model != self.cache.principal:
                model_list[model.DMeta.verbose_name_title] = name
        return model_list

    def get_dmodel(self, model, **query):
        return self.cache.models[model]
        if query:
            return model.objects.filter(**query)

