"""
Views do app inscricoes - Views para editais, inscrições e análises.

Este módulo contém as views da API REST para gestão de
editais, inscrições e análise de elegibilidade.
"""
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Edital, Inscricao, Analise
from .serializers import (
    EditalSerializer, 
    InscricaoSerializer, 
    AnaliseSerializer,
)
from core.models import Estudante


class EditalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD com Editais.
    
    Permite criar, listar, atualizar e deletar editais de inscrição.
    Inclui filtro para editais abertos.
    """
    queryset = Edital.objects.all()
    serializer_class = EditalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ativo']
    ordering_fields = ['data_abertura', 'data_fechamento']
    
    def get_queryset(self):
        """Retorna editais filtrados por parâmetro 'abertos'."""
        queryset = super().get_queryset()
        abertos = self.request.query_params.get('abertos', None)
        
        if abertos == 'true':
            agora = timezone.now()
            queryset = queryset.filter(
                ativo=True,
                data_abertura__lte=agora,
                data_fechamento__gte=agora
            )
        
        return queryset


class InscricaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD com Inscrições.
    
    Permite gerenciar inscrições de estudantes em editais,
    incluindo submissão e edição dentro do prazo.
    """
    queryset = Inscricao.objects.all()
    serializer_class = InscricaoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['edital', 'estudante', 'status']
    ordering_fields = ['criado_em', 'submetida_em']
    
    @action(detail=True, methods=['post'])
    def submeter(self, request, pk=None):
        """Submete a inscrição para análise."""
        inscricao = self.get_object()
        
        if not inscricao.pode_editar():
            return Response(
                {'error': 'Inscrição não pode mais ser editada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inscricao.status = 'SUBMETIDA'
        inscricao.submetida_em = timezone.now()
        inscricao.save()
        
        return Response({'status': 'Inscrição submetida com sucesso'})
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancela uma inscrição em rascunho."""
        inscricao = self.get_object()
        
        if inscricao.status != 'RASCUNHO':
            return Response(
                {'error': 'Apenas inscrições em rascunho podem ser canceladas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inscricao.delete()
        return Response({'status': 'Inscrição cancelada'})


class AnaliseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD com Análises.
    
    Permite que pedagogos analisem inscrições e decidam
    sobre a concessão de benefícios.
    """
    queryset = Analise.objects.all()
    serializer_class = AnaliseSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['deferida', 'elegivel']
    ordering_fields = ['data_analise']


class DashboardEstudanteView(APIView):
    """
    View para dashboard do estudante.
    
    Retorna todas as informações do estudante organizadas
    por eixos para exibição no dashboard.
    """
    
    def get(self, request, cpf):
        """Retorna dados do estudante para o dashboard."""
        try:
            estudante = Estudante.objects.get(cpf=cpf)
        except Estudante.DoesNotExist:
            return Response(
                {'error': 'Estudante não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        inscricoes = Inscricao.objects.filter(estudante=estudante)
        
        edital_aberto = Edital.objects.filter(
            ativo=True,
            data_abertura__lte=timezone.now(),
            data_fechamento__gte=timezone.now()
        ).first()
        
        ja_inscrito = False
        inscricao_atual = None
        
        if edital_aberto:
            ja_inscrito = inscricoes.filter(edital=edital_aberto).exists()
            if ja_inscrito:
                inscricao_atual = inscricoes.filter(edital=edital_aberto).first()
        
        dados_dashboard = {
            'estudante': {
                'nome': estudante.nome_completo,
                'matricula': estudante.matricula,
                'curso': estudante.curso,
                'campus': estudante.campus,
                'email': estudante.email_institucional,
            },
            'edital_aberto': EditalSerializer(edital_aberto).data if edital_aberto else None,
            'ja_inscrito': ja_inscrito,
            'inscricao_atual': InscricaoSerializer(inscricao_atual).data if inscricao_atual else None,
            'historico_inscricoes': InscricaoSerializer(inscricoes, many=True).data,
        }
        
        return Response(dados_dashboard)
