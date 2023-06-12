import csv
import os

from django.core.management.base import BaseCommand

from recieps.models import Ingredient

ALLOWED_MODELS = {
    'Ingridient': Ingredient,
}


class Command(BaseCommand):
    help = 'Load a csv file into the database'

    def _checker(self, model, path):
        error = False
        if not model:
            self.stderr.write(f"Model {model} is not in Allowed list")
            error = True 
        if not os.path.exists(path):
            self.stderr.write(f"File {path} doesn't exist")
            error = True
        if not path.endswith('.csv'):
            self.stderr.write(f"File {path} doesn't csv format")
            error = True
        if error:
            return False
        return True

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str, required=True, help="Name of ORM Model")
        parser.add_argument('--path', type=str, required=True, help="Path to the csv file")

    def handle(self, *args, **options):
        model = ALLOWED_MODELS.get(options['model'])
        path = options['path']
        if self._checker(model, path):
            with open(path, 'r') as f:
                reader = csv.reader(f, dialect='excel')
                for row in reader:
                    if row[0] and row[1]:
                        model.objects.get_or_create(
                            name=row[0],
                            measurement_unit=row[1],
                        )
            self.stdout.write("Loaded")
