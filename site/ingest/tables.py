
import os

import django_tables2 as tables

from django.urls import reverse

from ingest import models

CONFIRMED_CLASSES = {
    True: "table-success confirmed",
    False: "table-danger no-confirmed d-none"}


class RawFileTable(tables.Table):
    open = tables.Column(
        accessor="pk", verbose_name="Abrir",
        linkify=lambda record: reverse('ingest:check_file', args=[record.pk]))
    created = tables.Column(verbose_name="Fecha de creación")
    modified = tables.Column(verbose_name="Última modificación")
    file = tables.Column()
    file_size = tables.Column(accessor="file", verbose_name="Eventos en archivo")
    events = tables.Column(verbose_name="Eventos generados")

    class Meta:
        model = models.RawFile
        exclude = ["notes"]
        attrs = {
            "class": "table table-hover",
            "thead": {"class": "thead-dark"}}
        row_attrs = {
            "class": lambda record: CONFIRMED_CLASSES[record.confirmed]}
        sequence = ('id', 'created_by', "...", "open" )

    def render_open(self, value):
        return f"Ver #{value}"

    def render_created_by(self, value):
        if value.last_name and value.first_name:
            return f"{value.last_name}, {value.first_name} (@{value.username})"
        return f"@{value.username}"

    def render_file(self, value):
        return os.path.basename(value.file.name)

    def render_events(self, value):
        return value.count()

    def render_file_size(self, value, record):
        try:
            return len(record.as_df())
        except:
            return "Incorrecto"
