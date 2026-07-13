"""
Views do app core - ViewSets para Estudante e Endereco, e views de autenticação.

Este módulo contém as views da API REST para operações CRUD
com estudantes e endereços, além de views personalizadas para login.
"""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Estudante, Endereco, Usuario
from .serializers import EstudanteSerializer, EnderecoSerializer
from .forms import LoginForm, JornadaForm


class CustomLoginView(LoginView):
    """
    View personalizada para login com autopreenchimento de credenciais.
    Preenche automaticamente os campos com valores de demonstração.
    Redireciona pedagogos para o dashboard do pedagogo.
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
    
    def get_success_url(self):
        """
        Redireciona usuários pedagogo para o dashboard do pedagogo.
        Outros usuários vão para o admin ou URL padrão.
        """
        user = self.request.user
        if hasattr(user, 'is_pedagogo') and user.is_pedagogo:
            return '/pedagogo/dashboard/'
        return super().get_success_url()


def home_view(request):
    """
    View para página inicial do programa.
    """
    return render(request, 'home.html')


@login_required
def pedagogo_dashboard_view(request):
    """
    View para dashboard do pedagogo - lista todos os períodos (editais) do programa.
    Apenas usuários com is_pedagogo=True podem acessar.
    Permite editar e deletar editais.
    """
    # Verifica se o usuário é pedagogo
    if not hasattr(request.user, 'is_pedagogo') or not request.user.is_pedagogo:
        # Se não for pedagogo, redireciona para home ou mostra erro
        return render(request, 'core/sem_permissao.html')
    
    from inscricoes.models import Edital
    editais = Edital.objects.all().order_by('-criado_em')
    
    context = {
        'editais': editais,
    }
    
    return render(request, 'core/pedagogo_dashboard.html', context)


@login_required
def pedagogo_edital_detalhes_view(request, edital_id):
    """
    View para mostrar detalhes de um edital específico com todas as submissões dos estudantes.
    Apenas usuários com is_pedagogo=True podem acessar.
    """
    # Verifica se o usuário é pedagogo
    if not hasattr(request.user, 'is_pedagogo') or not request.user.is_pedagogo:
        return render(request, 'core/sem_permissao.html')
    
    from inscricoes.models import Edital, Inscricao
    edital = get_object_or_404(Edital, pk=edital_id)
    inscricoes = Inscricao.objects.filter(edital=edital).select_related('estudante').order_by('-criado_em')
    
    context = {
        'edital': edital,
        'inscricoes': inscricoes,
    }
    
    return render(request, 'core/pedagogo_edital_detalhes.html', context)


@login_required
def jornada_estudante_view(request):
    """
    View para o formulário de jornada do estudante.
    Permite ao estudante preencher seus dados em um fluxo contínuo.
    """
    if request.method == 'POST':
        form = JornadaForm(request.POST)
        if form.is_valid():
            # Salvar dados do estudante
            dados = form.cleaned_data
            
            # Criar ou atualizar estudante
            estudante, created = Estudante.objects.update_or_create(
                cpf=dados['cpf'],
                defaults={
                    'nome_completo': dados['nome_completo'],
                    'idade': dados['idade'],
                    'raca': dados.get('raca', ''),
                    'sexo': dados.get('sexo', ''),
                    'matricula': dados['matricula'],
                    'campus': dados['campus'],
                    'curso': dados['curso'],
                    'turno': dados['turno'],
                    'periodo': dados['periodo'],
                    'eh_cotista': dados.get('eh_cotista', False),
                    'moradia_estudantil': dados.get('moradia_estudantil', False),
                    'email_institucional': f"{dados['matricula']}@estudante.ifpe.edu.br",
                }
            )
            
            # Criar ou atualizar endereço
            Endereco.objects.update_or_create(
                estudante=estudante,
                defaults={
                    'cep': dados['cep'],
                    'bairro': dados['bairro'],
                    'cidade': dados['cidade'],
                    'estado': dados['estado'],
                }
            )
            
            messages.success(request, 'Jornada concluída com sucesso! Seus dados foram salvos.')
            return redirect('buscar_cpf')
    else:
        form = JornadaForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'core/jornada_estudante.html', context)


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
