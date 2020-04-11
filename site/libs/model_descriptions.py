
import json

import yaml

from django.conf import settings

PARSERS = {
    ".yaml": yaml.load,
    ".yml": yaml.load,
    ".json": json.load,
}


TYPES = {
    "number": models.IntegerField,
    "decimal": models.FloatField,
    "date": models.DateField,
    "bool": models.BooleanField,
    "text": models.CharField,
    "free": models.TextField,
}


def load_file(filename):
    ext = os.path.splitext(filename)[-1].lower()
    parser = PARSERS[ext]
    with open(filename) as fp:
        return parser(fp)


def from_description(*, filename, context):
    data = load_file(filename)
    # determinar y leer el formato del archivo
    # cargar los modelos
    # injectar modelos en el contexto
