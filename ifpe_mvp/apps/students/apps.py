"""
Aplicativo Students - Modelos e lógica de estudantes
"""
from django.apps import AppConfig


class StudentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ifpe_mvp.apps.students'
    verbose_name = 'Estudantes'
