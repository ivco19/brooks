# models.py
from django.db import models
from solo.models import SingletonModel


class ReportConfiguration(SingletonModel):
    class Meta:
        verbose_name = "Configuración de reporte"

    header = models.TextField(
        default="Generated with brooks", verbose_name="encabezado")
    footer = models.TextField(
        default="Generated at {{now}}", verbose_name="pie")