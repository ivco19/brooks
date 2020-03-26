
import os

from django.urls import reverse

from libs import dpprint

from ingest import models


class PatientPrinter(dpprint.ULPPrinter):
    class Meta:
        model = models.Patient
        exclude = ["notes", "modified"]

        order = ('id',)

