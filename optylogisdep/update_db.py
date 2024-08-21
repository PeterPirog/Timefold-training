import pandas as pd
from django.db import transaction, connection
import os
import sys
from typing import Type
from django.db.models import Model

# Add project root directory to sys.path
sys.path.append('G:/PycharmProject/Timefold-training/optylogisdep')

# Ensure the base directory of your project is included in sys.path
project_base_dir = 'G:/PycharmProject/Timefold-training'
sys.path.append(project_base_dir)

# Also include the 'modules' directory directly if needed
modules_dir = os.path.join(project_base_dir, 'optylogisdep', 'modules')
sys.path.append(modules_dir)

# Set Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.settings')

# Import Django and setup Django environment
import django

django.setup()

# Import your Django model
from optylogis.models import Pers_gr

def reset_id_sequence():
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='optylogis_pers_gr';")

def df_to_django_model(df: pd.DataFrame, DjangoModel: Type[Model]) -> None:
    with transaction.atomic():
        DjangoModel.objects.all().delete()
        reset_id_sequence()  # Resetowanie sekwencji ID

        for index, row in df.iterrows():
            obj = DjangoModel.objects.create(**row.to_dict())
            print(f"Created new record: {obj}")

    for obj in DjangoModel.objects.all():
        print(obj)

# Example usage:
df = pd.DataFrame({
    'pers_st_id': [1, 2],
    'ium': ['001', '002'],
    'nr_sw': ['101', '102'],
    'data_nad': [pd.Timestamp('2020-11-02'), pd.Timestamp('2021-11-02')],
    'zaw': [True, True],
    'cof': [False, True],
    'ost_sp': [pd.Timestamp('2021-11-02'), pd.Timestamp('2022-11-02')],
})

df_to_django_model(df, Pers_gr)

for obj in Pers_gr.objects.all():
    print(obj.__dict__)



def list_all_python_files(directory, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {'venv', 'venv32'}

    python_files = []
    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from traversal
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                python_files.append(full_path)
    return python_files

# Example usage:
project_directory = 'G:/PycharmProject/Timefold-training'  # Replace with your project directory
python_files = list_all_python_files(project_directory)

for file_path in python_files:
    print(file_path)

#from optylogisdep.modules.timefold_optimizer.tools.ODBCDataLoader import DataLoader
#from modules.timefold_optimizer.tools.ODBCDataLoader import DataLoader
from optylogisdep.modules.timefold_optimizer.tools.ODBCDataLoader import DataLoader

# from timefold_optimizer.tools.ODBCDataLoader import DataLoader


print(dir(DataLoader))