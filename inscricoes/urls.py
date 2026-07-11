"""
URLs do app inscricoes - Rotas para inscrições e editais.

Este módulo define as rotas da API REST para gestão de
editais, inscrições e análise de elegibilidade.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EditalViewSet,
    InscricaoViewSet,
    AnaliseViewSet,
    DashboardEstudanteView
)

# Router para gerar URLs automaticamente para ViewSets
router = DefaultRouter()
router.register(r'editais', EditalViewSet)
router.register(r'inscricoes', InscricaoViewSet)
router.register(r'analises', AnaliseViewSet)

urlpatterns = [
    # Inclui todas as rotas geradas pelo router
    path('', include(router.urls)),
    # Endpoint para dashboard do estudante
    path('dashboard/<str:cpf>/', DashboardEstudanteView.as_view(), name='dashboard-estudante'),
]
