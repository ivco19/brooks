import os

from django.core.management.base import BaseCommand, CommandError

from ingest import apps

import pandas as pd

PARSERS = {
    ".xlsx": pd.DataFrame.to_excel,
    ".csv": pd.DataFrame.to_csv
}


class Command(BaseCommand):
    help = "Create an empty spreadsheet to feed into the ingest models"

    def add_arguments(self, parser):
        parser.add_argument('out', type=str)

    def handle(self, out, *args, **options):
        dmodels = apps.IngestConfig.dmodels
        df = dmodels.make_empty_df()
        ext = os.path.splitext(out)[-1]
        parser = PARSERS.get(ext)
        if parser is None:
            raise CommandError(f"unknow fileformat '{out}'")
        parser(df, out, index=False)
