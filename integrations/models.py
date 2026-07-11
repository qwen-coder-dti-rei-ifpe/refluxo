"""
Models do app integrations - Modelos para integrações externas.

Este módulo contém modelos mock para simular dados das APIs
QAcadêmico e ConectaGov (CBC/CadÚnico) durante o desenvolvimento.
"""
from django.db import models


class QAcademicoMock(models.Model):
    """
    Modelo mock para simular dados da API QAcadêmico.
    
    Em produção, estes dados viriam da API real do QAcadêmico.
    Este modelo serve apenas para desenvolvimento e testes.
    """
    matricula = models.CharField(max_length=50, unique=True)
    nome_estudante = models.CharField(max_length=255)
    curso = models.CharField(max_length=200)
    campus = models.CharField(max_length=100)
    periodo = models.CharField(max_length=20)
    turno = models.CharField(max_length=20)
    status_matricula = models.CharField(max_length=20)
    data_consulta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "QAcadêmico Mock"
        verbose_name_plural = "QAcadêmico Mocks"
    
    def __str__(self):
        return f"{self.matricula} - {self.nome_estudante}"


class ConectaGovMock(models.Model):
    """
    Modelo mock para simular dados da API ConectaGov (CBC/CadÚnico).
    
    Em produção, estes dados viriam da API real do ConectaGov.
    Este modelo serve apenas para desenvolvimento e testes.
    """
    cpf = models.CharField(max_length=14, unique=True)
    nome_cidadao = models.CharField(max_length=255)
    nis = models.CharField(max_length=20, blank=True)
    possui_cadastro_unico = models.BooleanField(default=False)
    renda_per_capita = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    familiares = models.JSONField(default=list, blank=True)
    beneficios_sociais = models.JSONField(default=list, blank=True)
    data_consulta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "ConectaGov Mock"
        verbose_name_plural = "ConectaGov Mocks"
    
    def __str__(self):
        return f"{self.cpf} - {self.nome_cidadao}"
