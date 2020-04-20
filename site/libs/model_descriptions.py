import copy
import os
import json
import inspect

import yaml

from django.db import models
from django.core import validators
from django.conf import settings

from django_extensions.db.models import TimeStampedModel


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
                    raise KeyError(f"Duplicated key '{k}'")
                self[k] = v


# =============================================================================
# CONSTANTS
# =============================================================================

PARSERS = MultiKeyDict({
    (".yaml", ".yml"): yaml.load,
    (".json",): json.load,
})


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

    ("length", "max_length", "largo"): "max_length",
    ("default",): "default",
    ("unique", "unico", "único"): "unique",
    ("opciones", "choices"): "choices",
    ("min",): "min",
    ("max",): "max",

    ("related_name", "relacion", "relación"): "related_name",

    # FIELD_VALUES
    ("True", "true", "si", "Sí", "Si", "SI", "SÍ"): True,
    ("False", "false", "no", "No", "NO"): False,

})


NO_TRANSLATE = ["choices", "related_name"]


KEYS_TO_REMOVE = ["format", "tag"]


# =============================================================================
# FUNCTIONS
# =============================================================================

def load_file(filename):
    """Load the descfile based on the file extension"""
    ext = os.path.splitext(filename)[-1].lower()
    parser = PARSERS[ext]
    with open(filename) as fp:
        return parser(fp)


def translate(data):
    """Traduce todo lo que tiene el diccionario de datos
    si la llave traducida esta incluida en NO_TRANSLATE.

    """
    if isinstance(data, list):
        return [translate(e) for e in data]
    elif isinstance(data, dict):
        tdict = {}
        for k, v in data.items():
            tk = translate(k)
            tv = v if tk in NO_TRANSLATE else translate(v)
            tdict[tk] = tv
        return tdict
    return DATA_TRANSLATIONS.get(data, data)


def create_field(*, name, data, emodels):
    # copiamos los datos para manipular tranquilos
    data = copy.deepcopy(data)

    # primero sacamos el tipo
    ftype = data.pop("type")
    dj_ftype = FIELD_TYPES.get(ftype, ftype)

    # aca saco todos las configuraciones que se usaran vara parsear y no
    # para crear cosas
    for tr in KEYS_TO_REMOVE:
        data.pop(tr, None)

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
        link_to = emodels[dj_ftype]
        # we have a foreign key, si tiene "sep" es un many-to-many
        sep = data.pop("sep", None)
        if sep:
            return models.ManyToManyField(link_to, **data)
        else:
            return models.ForeignKey(
                link_to, on_delete=models.CASCADE, **data)


def create_model(*, name, data, emodels, module_spec):
    # copiamos los datos para manipular tranquilos
    data = copy.deepcopy(data)

    # creamos el contenedor de todos los atributos para el modelo
    attrs = {'__module__': module_spec.name}

    # iteramos sobre
    attributes = data.pop("attributes", {})
    for field_name, field_data in attributes.items():
        new_field = create_field(
            name=field_name, data=field_data, emodels=emodels)
        attrs[field_name] = new_field

    # creamos el modelo en si
    modelcls = type(name, (TimeStampedModel,), attrs)

    return modelcls


def from_description(*, descfile, context):

    # determinar y leer el formato del archivo
    data = load_file(descfile)

    # sacamos todos los modelos preexistentes en el contexto
    emodels = {
        k: v for k, v in context.items()
        if inspect.isclass(v) and issubclass(v, models.Model)}

    # buscamos en que modelo nos estan definiendo
    module_spec = context["__spec__"]

    # creamos los nuevos modelos en un nuevo diccionario
    for model_name, model_data in data.items():

        # traducimos las llaves del dicionario de datos
        tmodel_data =  translate(model_data)

        new_model = create_model(
            name=model_name, data=tmodel_data,
            emodels=emodels, module_spec=module_spec)
        emodels[model_name] = new_model

    # injectar modelos en el contexto
    context.update(emodels)

