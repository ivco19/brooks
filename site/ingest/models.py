
import os
import json

import dateutil

from django.db import models, transaction
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import FileExtensionValidator

from django_extensions.db.models import TimeStampedModel

import numpy as np

import pandas as pd

import pandas_interactive_html


# =============================================================================
# RAW FILE UPLOAD
# =============================================================================

def _raw_file_upload_to(instance, filename):
    folder = instance.created.strftime("%Y_%m")
    return '/'.join(["raw_files", folder, filename])


class RawFile(TimeStampedModel):
    PARSERS = {
        "csv": pd.read_csv,
        "xlsx": pd.read_excel,
    }
    EXTENSIONS = list(PARSERS)

    file = models.FileField(
        upload_to=_raw_file_upload_to,
        validators=[FileExtensionValidator(allowed_extensions=EXTENSIONS)],
        verbose_name="archivo")
    notes = models.TextField(blank=True, verbose_name="notas")
    confirmed = models.BooleanField(default=False, verbose_name="confirmado")

    created_by = models.ForeignKey(
        User, related_name="raw_files",
        on_delete=models.CASCADE, verbose_name="creado por")

    is_parsed = models.BooleanField(default=False, verbose_name="Parseado")

    @property
    def filename(self):
        return self.file.url.rsplit("/", 1)[-1]

    @property
    def ext(self):
        return os.path.splitext(self.filename)[-1]

    def as_df(self):
        parser = self.PARSERS[self.ext[1:]]
        return parser(self.file.path)

    def remove_events(self, commit=False):
        if commit and not self.is_parsed:
            raise ValueError(f"RawFile #{self.pk} no esta cargado")
        with transaction.atomic():
            self.events.all().delete()
            if commit:
                self.is_parsed = False
            else:
                transaction.set_rollback(True)


    def parse(self, commit=False):
        if commit and self.is_parsed:
            raise ValueError(f"RawFile #{self.pk} ya esta cargado")

        infos, errors, warnings = [], [], []

        try:
            df = self.as_df()
        except:
            df = pd.DataFrame()
            errors.append("No se pudo entender el archivo f'{self.pk}'")

        events_id = tuple(
            Event.objects.values_list("event_raw_file_id", flat=True))

        patients = Patient.objects.all()
        symptoms = Symptom.objects.all()
        sources = InfectionSource.objects.all()
        hospitals = Hospital.objects.all()
        travels = TravelFrom.objects.all()

        with transaction.atomic():
            # vamos creando un evento por ves
            for idx, row in df.iterrows():
                event = Event(raw_file=self, idx_raw_file=idx)

                pfx = f"Fila.{idx+1} >>"

                if row['Id_proc'] in events_id:
                    warnings.append(
                        f"{pfx} Id '{row['Id_proc']}' duplicado")
                    continue
                else:
                    event.event_raw_file_id = row['Id_proc']

                if row["Estado"] not in Event.STATUSES.values():
                    errors.append(
                        f"""{pfx} Estado '{row["Estado"]}' invalido""")
                    continue
                else:
                    event.status = row["Estado"]

                event.lock_address = row["Domicilio_Aislamiento"]

                event.first_simptoms_date = (
                    None
                    if pd.isnull(row["Fecha_comienzo_sintomas"]) else
                    dateutil.parser.parse(row["Fecha_comienzo_sintomas"]))

                event.confirmed_date = (
                    None
                    if pd.isnull(row["Fecha_confirmacion_positivo"]) else
                    dateutil.parser.parse(row["Fecha_confirmacion_positivo"]))

                event.discharge_date = (
                    None
                    if pd.isnull(row["Fecha_alta"]) else
                    dateutil.parser.parse(row["Fecha_alta"]))

                event.deceased_date = (
                    None
                    if pd.isnull(row["Fecha_fallecimiento"]) else
                    dateutil.parser.parse(row["Fecha_fallecimiento"]))

                event.has_simptoms = row["sintomatico"].lower() in ("si", "sí")

                # creo paciente
                p_id = row["Id_pac"]
                gender = row["genero"]
                age = int(row["Edad"])
                nationality = row["Nacionalidad"]
                address = row["Residencia"]

                patient, created = patients.get_or_create(
                    patient_raw_file_id=p_id)

                if created:
                    infos.append(
                        f"{pfx} Nuevo paciente '{p_id}'")
                else:
                    if patient.gender and patient.gender != gender:
                        warnings.append(
                            f"{pfx} Paciente '{p_id}' genero "
                            f"{patient.gender} -> {gender}")
                    if patient.age and patient.age != age:
                        warnings.append(
                            f"{pfx} Paciente '{p_id}' edad "
                            f"{patient.age} -> {age}")
                    if patient.nationality and patient.nationality != nationality:
                        warnings.append(
                            f"{pfx} Paciente '{p_id}' nacionalidad "
                            f"{patient.nationality} -> {nationality}")
                    if patient.address and patient.address != address:
                        warnings.append(
                            f"{pfx} Paciente '{p_id}' residencia "
                            f"{patient.address} -> {address}")

                patient.gender = gender
                patient.age = age
                patient.nationality = nationality
                patient.address = address

                event.patient = patient
                event.save()

                # hospital
                hname = str(row['Centro_salud']).lower().strip()
                if hname:
                    hospital, created = hospitals.get_or_create(name=hname)
                    if created:
                        infos.append(
                            f"{pfx} Nuevo Centro de salud '{hname}'")
                    event.hospital = hospital

                # isource
                isname = str(row['Fuente_de_infeccion']).lower().strip()
                if isname is not None:
                    infection_source, created = sources.get_or_create(name=isname)
                    if created:
                        infos.append(
                            f"{pfx} Nueva fuente de infeccion '{isname}'")
                    event.infection_source = infection_source# isource

                # travel
                tname = str(row['Origen']).lower().strip()
                if tname is not None:
                    travel_from, created = travels.get_or_create(name=tname)
                    if created:
                        infos.append(
                            f"{pfx} Nueva origen de viaje '{tname}'")
                    event.travel_from = travel_from

                # creo sintomas
                rsints = [
                    s.strip().lower() for s in str(row["sintomas"]).split(",")]
                for sname in rsints:
                    symptom, created = symptoms.get_or_create(name=sname)
                    if created:
                        infos.append(
                            f"{pfx} Nuevo Sintoma '{sname}'")
                    event.symptom.add(symptom)
            if commit:
                self.is_parsed = True
            else:
                transaction.set_rollback(True)

        resume = {"infos": infos, "errors": errors, "warnings": warnings}

        return resume


# =============================================================================
# REAL MODELS
# =============================================================================

class Patient(TimeStampedModel):

    patient_raw_file_id = models.IntegerField(
        unique=True, verbose_name="ID de archivo")
    gender = models.CharField(max_length=255, verbose_name="género")
    nationality = models.CharField(max_length=255, verbose_name="nacionalidad")
    address = models.CharField(max_length=255, verbose_name="dirección")
    notes = models.TextField(blank=True, verbose_name="notas", null=True)
    age = models.PositiveIntegerField(null=True)


class Symptom(TimeStampedModel):

    name = models.CharField(
        max_length=255, verbose_name="Nombre", unique=True)


class InfectionSource(TimeStampedModel):

    name = models.CharField(
        max_length=255, verbose_name="Nombre", null=True, unique=True)


class TravelFrom(TimeStampedModel):

    name = models.CharField(
        max_length=255, verbose_name="Nombre", null=True, unique=True)


class Hospital(TimeStampedModel):

    name = models.CharField(
        max_length=255, verbose_name="Nombre", null=True, unique=True)


class Event(TimeStampedModel):

    STATUSES = {
        "suspected": "Sospechoso",
        "active": "Activo",
        "recovered": "Recuperado",
        "deceased": "Fallecido"}

    raw_file = models.ForeignKey(
        RawFile, related_name="events",
        on_delete=models.CASCADE, verbose_name="Archivo")

    idx_raw_file = models.IntegerField(verbose_name="Indice en archivo")
    event_raw_file_id = models.IntegerField(
        unique=True, verbose_name="Id en archivo")
    patient = models.ForeignKey(
        Patient, related_name="events",
        on_delete=models.CASCADE, verbose_name="Paciente")
    symptom = models.ManyToManyField(Symptom, related_name="events")

    status = models.CharField(
        max_length=50, choices=list(STATUSES.items()))

    hospital = models.ForeignKey(Hospital, related_name="events", null=True,
        on_delete=models.CASCADE, verbose_name="Centro de salud")

    travel_from = models.ForeignKey(TravelFrom, related_name="events",
        on_delete=models.CASCADE, verbose_name="Origen", null=True)

    infection_source = models.ForeignKey(
        InfectionSource, related_name="events", null=True,
        on_delete=models.CASCADE, verbose_name="F. de Infección")

    lock_address = models.CharField(max_length=255)

    has_symptom = models.BooleanField(null=True)
    first_simptoms_date = models.DateField(null=True)
    confirmed_date = models.DateField(null=True)
    deceased_date = models.DateField(null=True)
    discharge_date = models.DateField(null=True)

"""

       'Centro_salud', 'Origen', 'Fuente_de_infeccion',

       """