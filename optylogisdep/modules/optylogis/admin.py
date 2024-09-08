# admin.py
from django.contrib import admin
from django.apps import apps
from . import models

# Funkcja automatyzująca dodawanie pól do list_display i search_fields
def auto_admin(model):
    class AutoAdmin(admin.ModelAdmin):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.list_display = [field.name for field in model._meta.get_fields()]
            self.search_fields = [field.name for field in model._meta.get_fields() if field.name != 'id']

        def __getattr__(self, name):
            if name.startswith('get_') and name.endswith('_admin'):
                field_name = name[4:-6]
                def getter(self, obj):
                    return getattr(obj, field_name)
                return getter
            raise AttributeError

    return AutoAdmin

# Rejestrowanie modeli z automatycznym dodawaniem pól
for model in apps.get_models():
    if model.__module__.startswith('optylogis.models'):
        admin.site.register(model, auto_admin(model))