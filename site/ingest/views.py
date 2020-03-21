from django.views.generic import CreateView, DetailView

from django.urls import reverse_lazy

from dashboard.views_mixins import LogginRequired

from . import models, forms


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


class CheckRawFileViewView(LogginRequired, DetailView):

    template_name = "ingest/CheckRawFileView.html"
    model = models.RawFile