
import os

import django_tables2 as tables

from django.urls import reverse

from ingest import models

CONFIRMED_CLASSES = {
    True: "table-success",
    False: "table-danger"}


class RawFileTable(tables.Table):
    open = tables.Column(
        accessor="pk", verbose_name="Abrir",
        linkify=lambda record: reverse('ingest:check_file', args=[record.pk]))
    created = tables.Column(verbose_name="Fecha de creación")
    modified = tables.Column(verbose_name="Última modificación")
    file = tables.Column()

    class Meta:
        model = models.RawFile
        exclude = ["notes"]
        attrs = {
            "class": "table table-hover",
            "thead": {"class": "thead-dark"}}
        row_attrs = {
            "class": lambda record: CONFIRMED_CLASSES[record.confirmed]}
        sequence = ('id', 'created_by', )

    def render_open(self, value):
        return f"Ver #{value}"

    def render_created_by(self, value):
        if value.last_name and value.first_name:
            return f"{value.last_name}, {value.first_name} (@{value.username})"
        return f"@{value.username}"

    def render_file(self, value):
        return os.path.basename(value.file.name)
