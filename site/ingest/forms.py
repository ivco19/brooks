from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django_summernote.widgets import SummernoteInplaceWidget

from . import models


class UploadRawFileForm(forms.ModelForm):
    class Meta:
        model = models.RawFile
        fields = ('file', "notes")
        widgets = {
            'notes': SummernoteInplaceWidget(
                attrs={'summernote': {'width': '100%', 'height': '200px'}})}


    placeholders = {
        "file": "Nuevo archivo con los datos",
        "notes": "Alguna nota en particular sobre el archivo",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Subir archivo'))

        for name, field in self.fields.items():
            field.required = False
            field.widget.attrs['placeholder'] = self.placeholders.get(
                name, field.label)


class UpdateRawFileForm(forms.ModelForm):
    class Meta:
        model = models.RawFile
        fields = ("notes", "confirmed")
        widgets = {
            'notes': SummernoteInplaceWidget(
                attrs={'summernote': {'width': '100%', 'height': '200px'}})}

    placeholders = {
        "notes": "Alguna nota en particular sobre el archivo",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = "rawFileForm"

        for name, field in self.fields.items():
            field.required = False
            field.widget.attrs['placeholder'] = self.placeholders.get(
                name, field.label)


class PatientDetailForm(forms.ModelForm):
    class Meta:
        model = models.Patient
        fields = ("notes",)
        widgets = {
            'notes': SummernoteInplaceWidget(
                attrs={'summernote': {'width': '100%', 'height': '200px'}})}

    placeholders = {
        "notes": "Alguna nota en particular sobre el paciente",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Guardar Notas'))

        for name, field in self.fields.items():
            field.required = False
            field.widget.attrs['placeholder'] = self.placeholders.get(
                name, field.label)