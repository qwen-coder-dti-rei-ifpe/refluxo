"""
URLs do app integrations - Rotas para integrações com APIs externas.

Este módulo define as rotas da API REST para integrações com
QAcadêmico, ConectaGov (CBC/CadÚnico) e OAuth.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QAcademicoViewSet, 
    ConectaGovViewSet, 
    ConsultaElegibilidadeView,
    OAuthTokenView,
    DadosFamiliarView
)

# Router para gerar URLs automaticamente para ViewSets
router = DefaultRouter()
router.register(r'qacademico', QAcademicoViewSet, basename='qacademico')
router.register(r'conecta-gov', ConectaGovViewSet, basename='conecta-gov')

urlpatterns = [
    # Inclui todas as rotas geradas pelo router
    path('', include(router.urls)),
    # Endpoint para obtenção de token OAuth
    path('api-cpf-light/v2/oauth2/token/', OAuthTokenView.as_view(), name='oauth-token'),
    # Endpoint para consulta de dados familiares do CadÚnico
    path('api-cadunico-servicos-dados/v1/dp/dadosFamiliar/<str:cpf>/', DadosFamiliarView.as_view(), name='dados-familiar'),
    # Endpoint para consulta de elegibilidade
    path('consulta-elegibilidade/', ConsultaElegibilidadeView.as_view(), name='consulta-elegibilidade'),
]
