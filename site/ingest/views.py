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

import string
import random
import os
import itertools as it
import datetime as dt

from django.conf import settings

from django.views.generic import CreateView, UpdateView, DetailView, View
from django.urls import reverse_lazy, reverse

from django.http import HttpResponse

from django.db.models.fields.files import FieldFile
from django.db.models import (
    ForeignKey, TextField, ManyToManyField, ManyToOneRel, ManyToManyRel)

from django.utils.html import format_html

from django.contrib.auth.models import User
from django.apps import apps

from django_tables2.views import SingleTableView

from django_pandas.io import read_frame

import humanize

from brooks.views_mixins import LogginRequired, CacheMixin
from brooks.libs.dmatplotlib import MatplotlibView

from ingest.libs.mdesc import is_name_forbidden
from ingest import models, forms, tables


# =============================================================================
# CONSTANTS
# =============================================================================

LETTERS = string.ascii_uppercase + string.digits

app = apps.get_app_config("ingest")


# =============================================================================
# CLASSES
# =============================================================================

class UploadRawFileView(LogginRequired, CreateView):

    model = models.RawFile
    form_class = forms.UploadRawFileForm
    template_name = "ingest/UploadRawFile.html"
    success_message = "Archivo ({id}) '{filename}' subido con éxito"

    def get_success_url(self):
        rawfile = self.object
        return reverse_lazy('ingest:check_file', args=[rawfile.pk])

    def get_success_message(self, cleaned_data):
        return self.success_message.format(
            id=self.object.id, filename=self.object.filename)

    def form_valid(self, form):
        rawfile = form.save(commit=False)
        rawfile.created_by = self.request.user
        rawfile.modify_by = self.request.user
        rawfile.save()

        return super().form_valid(form)


class DownloadEmptyView(LogginRequired, CacheMixin, View):
    content_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    cache_timeout = 60 * 2

    def get(self, *args, **kwargs):

        today = dt.datetime.now().date()

        response = HttpResponse(content_type=self.content_type)
        fname = f"planilla_brooks_{today.isoformat()}.xlsx"
        response['Content-Disposition'] = f'attachment; filename={fname}'

        df = app.ingestor.make_empty_df()
        df.to_excel(response)

        return response


class CheckRawFileView(LogginRequired, UpdateView):

    template_name = "ingest/CheckRawFileView.html"
    form_class = forms.UpdateRawFileForm
    model = models.RawFile
    success_url = reverse_lazy("ingest:list_files")

    def get_context_data(self):
        context_data = super().get_context_data()

        if self.object.broken:
            context_data["merge_info"] = None
            context_data["df"] = pd.DataFrame()

        elif not self.object.merged:
            mmd = app.ingestor.merge_info(
                user=self.request.user,
                raw_file=self.object)
            context_data["merge_info"] = mmd
            context_data["df"] = self.object.as_df()

        else:
            context_data["df"] = self.object.as_df()

        context_data["conf_code"] = "".join(random.sample(LETTERS, 6))
        return context_data

    def form_valid(self, form):
        rawfile = form.save(commit=False)
        rawfile.modify_by = self.request.user
        rawfile.save()
        return super().form_valid(form)


class ListRawFileView(LogginRequired, SingleTableView):

    model = models.RawFile
    table_class = tables.RawFileTable
    template_name = "ingest/ListRawFileView.html"


# =============================================================================
# THE DYNAMIC VIEWS HERE
# =============================================================================

class IngestViewMixin:

    def get_dmodel(self):
        model_name = self.kwargs["dmodel"]
        return app.get_model(model_name=model_name)


class ListDModelView(LogginRequired, IngestViewMixin, SingleTableView):
    table_class = None
    template_name = "ingest/ListDModelView.html"

    def get_queryset(self, *args, **kwargs):
        return self.get_dmodel().objects.all()

    def get_table_class(self, *args, **kwargs):
        dmodel = self.get_dmodel()

        # columna de abrir
        def open_linkify(record):
            return reverse(
                'ingest:dmodel_details',
                args=[dmodel.__name__, record.pk])

        open_column = tables.Column(
            accessor="pk", verbose_name="Abrir", linkify=open_linkify)

        def render_open(self, value):
            return f"Ver {dmodel._meta.verbose_name_plural.title()}"

        # columnas de creacion y modificacion
        created = tables.Column(verbose_name="Fecha de creación")
        modified = tables.Column(verbose_name="Última modificación")

        # metaclass
        class Meta:
            model = dmodel
            attrs = {
                "id": "dtable",
                "class": "table table-hover",
                "thead": {"class": "thead-dark"}}
            sequence = ('id', "...", "open")

        # creamos la clase
        table_name = f"{dmodel.__name__}Table"
        bases = (tables.Table,)
        attrs = {
            "open": open_column,
            "created": created,
            "modified": modified,
            "render_open": render_open,
            "Meta": Meta}

        # si la clase es principal hay que agregarle un par de renders
        if dmodel.principal:
            def render_created_by(self, value):
                if value.last_name and value.first_name:
                    return (
                        f"{value.last_name}, {value.first_name}"
                        f"(@{value.username})")
                return f"@{value.username}"

            def render_raw_file(self, value):
                return os.path.basename(value.file.name)

            attrs.update({
                "render_created_by": render_created_by,
                "render_raw_file": render_raw_file})

        table_cls = type(table_name, bases, attrs)
        return table_cls

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["dmodel"] = self.get_dmodel()
        return context


class PlotDModelView(LogginRequired, IngestViewMixin, MatplotlibView):

    template_name = "ingest/PlotDModelView.html"
    draw_methods = [
        "draw_creation_time"]
    plot_format = "png"
    tight_layout = True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["dmodel"] = self.get_dmodel()
        return context

    def get_draw_context(self):
        dmodel = self.get_dmodel()
        df = read_frame(dmodel.objects.all())
        return {"dmodel": dmodel, "queryset": dmodel.objects.all(), "df": df}

    def sin_datos(self, fig, ax):
        ax.text(
            0.6, 0.7, "Datos", size=50, rotation=30., ha="center", va="center",
            bbox={
                "boxstyle": "round",
                "ec": (1., 0.5, 0.5),
                "fc": (1., 0.8, 0.8)})

        ax.text(
            0.5, 0.5, "Sin", size=50, rotation=-25., ha="right", va="top",
            bbox={
                "boxstyle": "round",
                "ec": (1., 0.5, 0.5),
                "fc": (1., 0.8, 0.8)})

        ax.set_yticks([])
        ax.set_xticks([])

    def draw_creation_time(self, dmodel, df, queryset, fig, ax, **kwargs):
        dmodel_name = dmodel.verbose_name_plural()

        ax.set_title(f"{dmodel_name} creados y modificados por fecha")
        ax.set_ylabel(f"Número de {dmodel_name}")
        ax.set_xlabel("Fecha")

        if not queryset.exists():
            self.sin_datos(fig, ax)
            return

        datac, datam = {}, {}
        for instance in queryset:
            created = instance.created.date()
            datac[created] = datac.setdefault(created, 0) + 1

            modified = instance.modified.date()
            datam[modified] = datam.setdefault(modified, 0) + 1

        # for idx in range(10):
        #     import datetime as dt
        #     import random
        #     now = (dt.datetime.now() + dt.timedelta(days=idx)).date()
        #     datac[now] = random.randint(1, 100)
        #     datam[now] = random.randint(1, 100)

        ax.plot(
            [k.isoformat() for k in datac.keys()],
            list(datac.values()), ls="--", marker="o", label="Creados")

        ax.plot(
            [k.isoformat() for k in datam.keys()],
            list(datam.values()), ls="--", marker="o", label="Modificados")

        xtick_labels = [l for l in sorted(it.chain(datac, datam))]
        ax.set_xticklabels(xtick_labels, rotation=45)

        ax.legend()


class DetailDModelView(LogginRequired, IngestViewMixin, DetailView):

    template_name = "ingest/DetailDModelView.html"

    CUSTOM_LABELS = {
        "created": "Fecha de creación",
        "modified": "Fecha de modificación",
    }

    FORMATTERS = {
        FieldFile: lambda v: os.path.basename(v.name),
        dt.date: humanize.naturaldate,
        dt.datetime: humanize.naturaldate,
        bool: lambda v: "Sí" if v else "No"
    }

    def get_queryset(self, *args, **kwargs):
        return self.get_dmodel().objects.all()

    def get_label(self, fname, dj_field):
        if isinstance(dj_field, (ManyToOneRel, ManyToManyRel)):
            return dj_field.related_model._meta.verbose_name_plural.title()
        label = dj_field.verbose_name
        label = self.CUSTOM_LABELS.get(label, label)
        return label.title()

    def format_value(self, value, dj_type):
        humanize.i18n.activate("es_ES")
        ftype = type(value)
        formatter = self.FORMATTERS.get(ftype, str)
        fvalue = formatter(value)
        if isinstance(dj_type, TextField):
            fvalue = format_html(fvalue)
        return fvalue

    def make_resume(self, instance, idf, is_dmodel, props):
        if isinstance(instance, User):
            return f"@{instance.username} (# {instance.pk}))"
        elif isinstance(instance, models.RawFile):
            filename = os.path.basename(instance.file.name)
            return f"{filename} (# {instance.pk})"
        if is_dmodel and idf:
            return f"{getattr(instance, idf)} (# {instance.pk})"
        return f"(# {instance.pk})"

    def split_dminstance(self, instance, check_forbidden=False, related=True):

        identifier = getattr(instance, "identifier", None)
        is_dmodel = True

        dj_fields = {f.name: f for f in instance._meta.get_fields()}

        props, lout, lin = {}, {}, {}
        for fname, dj_field in dj_fields.items():
            if check_forbidden and is_name_forbidden(fname):
                continue

            vname = self.get_label(fname, dj_field)

            if isinstance(dj_field, ForeignKey):
                if not related:
                    continue

                sinstance = getattr(instance, fname)
                value = self.split_dminstance(
                    sinstance, check_forbidden=True, related=False)
                lout[fname] = {
                    "label": vname,
                    "value": value}

            elif isinstance(dj_field, ManyToManyField):
                if not related:
                    continue

                values = []
                accessor = getattr(instance, fname)
                for sinstance in accessor.all():
                    value = self.split_dminstance(
                        sinstance, check_forbidden=True, related=False)
                    values.append(value)
                lin[fname] = {"label": vname, "value": values}

            elif isinstance(dj_field, (ManyToOneRel, ManyToManyRel)):
                if not related:
                    continue

                values = []
                accessor_name = dj_field.get_accessor_name()
                accessor = getattr(instance, accessor_name)
                for sinstance in accessor.all():
                    value = self.split_dminstance(
                        sinstance, check_forbidden=True, related=False)
                    values.append(value)
                lin[fname] = {"label": vname, "value": values}

            elif dj_field:
                value = getattr(instance, fname)
                value = self.format_value(value=value, dj_type=dj_field)
                props[fname] = {"label": vname, "value": value or "--"}

        identifier = props.get(identifier)
        desc_name = instance.__class__.__name__

        resume = self.make_resume(
            instance=instance, is_dmodel=is_dmodel,
            idf=identifier, props=props)

        return {
            "resume": resume,
            "is_dmodel": is_dmodel,
            "desc_name": desc_name,
            "idf": {
                "label": identifier or "",
                "value": getattr(instance, identifier) if identifier else ""},
            "pk": instance.pk,
            "props": props,
            "lin": lin,
            "lout": lout}

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data["dmodel"] = self.get_dmodel()
        context_data["objd"] = self.split_dminstance(
            instance=context_data["object"])
        return context_data
