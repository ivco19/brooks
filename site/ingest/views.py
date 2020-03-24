import string
import random

from django.views.generic import CreateView, UpdateView

from django.urls import reverse_lazy

from brooks.views_mixins import LogginRequired

from . import models, forms

LETTERS = string.ascii_uppercase + string.digits


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
            rawfile.save()
            return super().form_valid(form)


class CheckRawFileView(LogginRequired, UpdateView):

    template_name = "ingest/CheckRawFileView.html"
    form_class = forms.UpdateRawFileForm
    model = models.RawFile

    def get_context_data(self):
        context_data = super().get_context_data()
        context_data["conf_code"] = "".join(random.sample(LETTERS, 6))
        return context_data
