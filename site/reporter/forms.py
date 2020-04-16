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

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django_summernote.widgets import SummernoteInplaceWidget


from reporter import models


# =============================================================================
# CLASSES
# =============================================================================

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
