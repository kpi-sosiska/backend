import contextlib
import os
from pathlib import Path

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garni_studenti.settings')
django.setup()

import csv


@contextlib.contextmanager
def reader(name):
    file_path = Path(__file__).parent / (name + '.csv')

    with file_path.open() as csv_file:
        csv_reader = csv.reader(csv_file)
        yield csv_reader