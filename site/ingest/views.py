import string
import random
import os
import itertools as it

from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy, reverse

from django_tables2.views import SingleTableView

from django_pandas.io import read_frame

from brooks.views_mixins import LogginRequired
from brooks.libs.dmatplotlib import MatplotlibView

from ingest import apps, models, forms, tables

# =============================================================================
# CONSTANTS
# =============================================================================

LETTERS = string.ascii_uppercase + string.digits


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
        try:
            filepath = rawfile.file.path
            df = apps.IngestConfig.dmodels.load_data_file(filepath)
            rawfile.size = len(df)
        except Exception:
            pass
        rawfile.save()
        return super().form_valid(form)


class CheckRawFileView(LogginRequired, UpdateView):

    template_name = "ingest/CheckRawFileView.html"
    form_class = forms.UpdateRawFileForm
    model = models.RawFile
    success_url = reverse_lazy("ingest:list_files")

    def get_context_data(self):
        context_data = super().get_context_data()
        dmodels = apps.IngestConfig.dmodels
        if not self.object.merged:
            mmd = dmodels.merge_info(
                created_by=self.request.user, raw_file=self.object)
            context_data["merge_info"] = mmd.merge_info
            context_data["df"] = mmd.df
        else:
            filepath = self.object.file.path
            context_data["df"] = dmodels.load_data_file(filepath)
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


class ListDmodelView(LogginRequired, SingleTableView):

    model = None
    table_class = None
    template_name = "ingest/ListDModelView.html"

    def get_table_class(self, *args, **kwargs):
        dmodel = self.get_dmodel()

        # columna de abrir
        def open_linkify(record):
            return reverse('ingest:check_file', args=[record.pk])

        open_column = tables.Column(
            accessor="pk", verbose_name="Abrir", linkify=open_linkify)

        def render_open(self, value):
            return f"Ver {dmodel.DMeta.desc_name}"

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
        table_name = f"{dmodel.DMeta.desc_name}Table"
        bases = (tables.Table,)
        attrs = {
            "open": open_column,
            "created": created,
            "modified": modified,
            "render_open": render_open,
            "Meta": Meta}

        # si la clase es principal hay que agregarle un par de renders
        if dmodel.DMeta.principal:
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

    def get_dmodel(self):
        dmodel_name = self.kwargs["dmodel"]
        return apps.IngestConfig.dmodels.get_dmodel(dmodel_name)

    def get_queryset(self, *args, **kwargs):
        dmodel = self.get_dmodel()
        return dmodel.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["dmodel"] = self.get_dmodel()
        return context


class PlotDmodelView(LogginRequired, MatplotlibView):

    template_name = "ingest/PlotDModelView.html"
    draw_methods = [
        "draw_creation_time"]
    plot_format = "png"
    tight_layout = True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["dmodel"] = self.get_dmodel()
        return context

    def get_dmodel(self):
        dmodel_name = self.kwargs["dmodel"]
        return apps.IngestConfig.dmodels.get_dmodel(dmodel_name)

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
        dmodel_name = dmodel.DMeta.verbose_name_title

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


# class PatientDetailView(LogginRequired, UpdateView):

#     template_name = "ingest/PatientDetailView.html"
#     form_class = forms.PatientDetailForm
#     model = models.Patient

#     def get_success_url(self):
#         patient = self.object
#         return reverse_lazy('ingest:patient_detail', args=[patient.pk])

#     def get_context_data(self):
#         context_data = super().get_context_data()
#         context_data["pp_patient"] = pprinter.PatientPrinter(self.object)
#         return context_data
