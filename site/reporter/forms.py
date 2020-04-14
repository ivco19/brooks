from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django_summernote.widgets import SummernoteInplaceWidget


from . import models


class ReportConfigurationForm(forms.ModelForm):
    class Meta:
        model = models.ReportConfiguration
        fields = ('header', 'footer')
        widgets = {
            'header': SummernoteInplaceWidget(
                attrs={'summernote': {'width': '100%', 'height': '200px'}}),
            'footer': SummernoteInplaceWidget(
                attrs={'summernote': {'width': '100%', 'height': '200px'}}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Guardar'))
