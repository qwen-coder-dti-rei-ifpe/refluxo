"""
Views do app core - ViewSets para Estudante e Endereco.

Este módulo contém as views da API REST para operações CRUD
com estudantes e endereços.
"""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from .models import Estudante, Endereco
from .serializers import EstudanteSerializer, EnderecoSerializer


def home_view(request):
    """
    View para página inicial do programa.
    """
    return render(request, 'home.html')


def buscar_cpf_view(request):
    """
    View para página de busca de estudante por CPF.
    """
    cpf_search = request.GET.get('cpf', '')
    estudante = None
    error = None
    
    if cpf_search:
        # Remove caracteres não numéricos do CPF
        cpf_limpo = ''.join(filter(str.isdigit, cpf_search))
        
        if len(cpf_limpo) != 11:
            error = 'CPF deve conter 11 dígitos.'
        else:
            try:
                estudante = Estudante.objects.select_related('endereco').get(cpf=cpf_limpo)
            except Estudante.DoesNotExist:
                pass  # Não mostra erro, apenas não encontra resultado
    
    context = {
        'cpf_search': cpf_search,
        'estudante': estudante,
        'error': error,
    }
    
    return render(request, 'buscar_cpf.html', context)


def buscar_matricula_view(request):
    """
    View para página de busca de estudante por matrícula.
    """
    matricula_search = request.GET.get('matricula', '')
    estudante = None
    error = None
    
    if matricula_search:
        try:
            estudante = Estudante.objects.select_related('endereco').get(matricula=matricula_search)
        except Estudante.DoesNotExist:
            error = 'Estudante com esta matrícula não encontrado.'
    
    context = {
        'matricula_search': matricula_search,
        'estudante': estudante,
        'error': error,
    }
    
    return render(request, 'buscar_matricula.html', context)


class EstudanteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD com Estudante.
    
    Permite buscar estudantes por matrícula ou CPF,
    além de listar, criar, atualizar e deletar registros.
    """
    queryset = Estudante.objects.all()
    serializer_class = EstudanteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['matricula', 'cpf']
    search_fields = ['nome_completo', 'matricula', 'cpf']


class EnderecoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD com Endereco.
    
    Permite gerenciar endereços dos estudantes,
    vinculados através de relação OneToOne.
    """
    queryset = Endereco.objects.all()
    serializer_class = EnderecoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['estudante', 'cidade', 'estado']
