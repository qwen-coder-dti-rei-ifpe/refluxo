"""
Views do app core - ViewSets para Estudante e Endereco, e views de autenticação.

Este módulo contém as views da API REST para operações CRUD
com estudantes e endereços, além de views personalizadas para login.
"""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .models import Estudante, Endereco
from .serializers import EstudanteSerializer, EnderecoSerializer
from .forms import LoginForm


class CustomLoginView(LoginView):
    """
    View personalizada para login com autopreenchimento de credenciais.
    Preenche automaticamente os campos com valores de demonstração.
    """
    form_class = LoginForm
    template_name = 'registration/login.html'
    
    def get_initial(self):
        """
        Retorna dados iniciais para autopreencher o formulário de login.
        """
        initial = super().get_initial()
        # Autopreenche com credenciais de demonstração
        initial['username'] = '12345678900'
        initial['password'] = '123'
        return initial


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
