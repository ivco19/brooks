
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
    size = tables.Column(verbose_name="Registros")
    rcreated = tables.Column(verbose_name="Registros generados")

    class Meta:
        model = models.RawFile
        exclude = ["notes"]
        attrs = {
            "class": "table table-hover",
            "thead": {"class": "thead-dark"}}
        row_attrs = {
            "class": lambda record: CONFIRMED_CLASSES[record.merged]}
        sequence = ('id', 'created_by', "...", "open")

    def render_open(self, value):
        return f"Ver #{value}"

    def render_created_by(self, value):
        if value.last_name and value.first_name:
            return f"{value.last_name}, {value.first_name} (@{value.username})"
        return f"@{value.username}"

    def render_file(self, value):
        return os.path.basename(value.file.name)

    def render_rcreated(self, value):
        return value.count()

    def render_size(self, value, record):
        try:
            return record.size
        except Exception:
            return "Incorrecto"


# =============================================================================
# PACIENTES
# =============================================================================

# PATIENT_CLASSES = {
#     "active": "table-warning active",
#     "deceased": "table-danger deceased d-none",
#     "recovered": "table-success recovered d-none",
#     "suspected": "table-info suspected",
# }


# class PatientTable(tables.Table):
#     open = tables.Column(
#         accessor="pk", verbose_name="Abrir",
#         linkify=lambda record: reverse(
#                     'ingest:patient_detail', args=[record.pk]))

#     created = tables.Column(verbose_name="Fecha de creación")
#     events = tables.Column(verbose_name="Eventos")

#     hospital = tables.Column(verbose_name="C.Salud")
#     last_event = tables.Column(verbose_name="U.Evento")
#     last_status = tables.Column(verbose_name="Estado")

#     class Meta:
#         model = models.Patient
#         exclude = ["notes", "modified"]
#         attrs = {
#             "class": "table table-hover",
#             "thead": {"class": "thead-dark"}}
#         row_attrs = {
#             "class": lambda record: PATIENT_CLASSES[record.last_status]}
#         sequence = ('id', "...", "open" )

#     def render_events(self, record):
#         return record.events.count()

#     def last_event(self, value):
#         return value.created

#     def render_hospital(self, record):
#         return record.last_event.hospital.name

#     def render_last_status(self, value):
#         return models.Event.STATUSES[value]
