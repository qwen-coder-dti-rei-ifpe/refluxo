"""
Aplicativo Enrollments - Modelos e lógica de inscrições no programa
"""
from django.apps import AppConfig


class EnrollmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ifpe_mvp.apps.enrollments'
    verbose_name = 'Inscrições'
