from django.views.generic import UpdateView

from brooks.views_mixins import LogginRequired

from reporter import models, forms


class ReportConfigurationView(LogginRequired, UpdateView):
    model = models.ReportConfiguration
    form_class = forms.ReportConfigurationForm
    template_name = "reporter/ReportConfiguration.html"
    success_message = "Configuración de reportes exitosa"


    def get_object(self):
        return models.ReportConfiguration.get_solo()
