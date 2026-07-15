"""
Aplicativo Family - Modelos e lógica de familiares do grupo familiar
"""
from django.apps import AppConfig


class FamilyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ifpe_mvp.apps.family'
    verbose_name = 'Grupo Familiar'
