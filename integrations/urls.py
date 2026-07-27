"""
URLs do app integrations - Rotas para integrações com APIs externas.

Este módulo define as rotas da API REST para integrações com
QAcadêmico, ConectaGov (CBC/CadÚnico) e OAuth2.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QAcademicoViewSet, 
    ConectaGovViewSet, 
    ConsultaElegibilidadeView,
    OAuth2TokenView,
)

# Router para gerar URLs automaticamente para ViewSets
router = DefaultRouter()
router.register(r'qacademico', QAcademicoViewSet, basename='qacademico')
router.register(r'conecta-gov', ConectaGovViewSet, basename='conecta-gov')

urlpatterns = [
    # Inclui todas as rotas geradas pelo router
    path('', include(router.urls)),
    # Endpoint para consulta de elegibilidade
    path('consulta-elegibilidade/', ConsultaElegibilidadeView.as_view(), name='consulta-elegibilidade'),
    # Endpoint OAuth2 para geração de token JWT
    path('api-cpf-light/v2/oauth2/token', OAuth2TokenView.as_view(), name='oauth2-token'),
]
