import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

ALLOWED_MODELS = {
    'Ingredient': Ingredient,
}


class Command(BaseCommand):
    '''
    Custom management command for load data into the Models from CSV file
    using: python manage.py import_csv --model <model_name> --path <path_to_the_file>.csv
    '''
    help = 'Load a csv file into the database'

    def _checker(self, model, path):
        if model not in ALLOWED_MODELS:
            self.stderr.write(f"Model {model} is not in Allowed list") 
            return False
        if not os.path.exists(path):
            self.stderr.write(f"File {path} doesn't exist")
            return False
        if not path.endswith('.csv'):
            self.stderr.write(f"File {path} doesn't csv format")
            return False
        return True

    def add_arguments(self, parser):
        parser.add_argument('--model', type=str, required=True, help="Name of ORM Model")
        parser.add_argument('--path', type=str, required=True, help="Path to the csv file")

    def handle(self, *args, **options):
        model = options['model']
        path = options['path']
        if self._checker(model, path):
            model = ALLOWED_MODELS[model]
            with open(path, 'r') as f:
                reader = csv.reader(f, dialect='excel')
                for name, measure in reader:
                    if name and measure:
                        model.objects.get_or_create(
                            name=name,
                            measurement_unit=measure,
                        )
            self.stdout.write("Loaded")
