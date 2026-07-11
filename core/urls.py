"""
URLs do app core - Rotas para estudante e endereço.

Este módulo define as rotas da API REST para operações com
dados de estudantes e endereços.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EstudanteViewSet, EnderecoViewSet

# Router para gerar URLs automaticamente para ViewSets
router = DefaultRouter()
router.register(r'estudantes', EstudanteViewSet)
router.register(r'enderecos', EnderecoViewSet)

urlpatterns = [
    # Inclui todas as rotas geradas pelo router
    path('', include(router.urls)),
]
