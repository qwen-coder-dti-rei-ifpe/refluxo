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
        Verifica o parâmetro 'tipo' na URL para decidir quais credenciais usar.
        """
        initial = super().get_initial()
        tipo = self.request.GET.get('tipo', 'estudante')
        
        if tipo == 'pedagogo':
            # Credenciais de teste para pedagogo
            initial['username'] = 'pedagogo'
            initial['password'] = 'pedagogo123'
        else:
            # Credenciais de teste para estudante
            initial['username'] = '12345678900'
            initial['password'] = '123'
        
        return initial
    
    def get_success_url(self):
        """
        Redireciona usuários para seus dashboards específicos baseados no tipo de usuário.
        - Estudantes: redireciona para /dashboard/student/
        - Assistentes sociais: redireciona para /dashboard/assistente/
        - Outros: usa a URL padrão ou admin
        """
        user = self.request.user
        
        # Verifica se é assistente social
        if hasattr(user, 'is_assistente_social') and user.is_assistente_social:
            return '/dashboard/assistente/'
        
        # Verifica se é estudante (busca pelo CPF do usuário no modelo Estudante)
        from core.models import Estudante
        if hasattr(user, 'cpf') and user.cpf:
            if Estudante.objects.filter(cpf=user.cpf).exists():
                return '/dashboard/student/'
        
        # Caso contrário, usa a URL padrão do Django
        return super().get_success_url()


def home_view(request):
    """
    View para página inicial do programa.
    """
    return render(request, 'home.html')


@login_required
def assistente_dashboard_view(request):
    """
    View para dashboard do assistente social - lista todos os períodos (editais) do programa.
    Apenas usuários com is_assistente_social=True podem acessar.
    Permite editar e deletar editais.
    """
    # Verifica se o usuário é assistente social
    if not hasattr(request.user, 'is_assistente_social') or not request.user.is_assistente_social:
        # Se não for assistente social, redireciona para dashboard do estudante
        return redirect('/dashboard/student/')
    
    from inscricoes.models import Edital
    editais = Edital.objects.all().order_by('-criado_em')
    
    context = {
        'editais': editais,
    }
    
    return render(request, 'core/pedagogo_dashboard.html', context)


@login_required
def student_dashboard_view(request):
    """
    View para dashboard do estudante.
    Primeiro o estudante deve selecionar um edital ativo, depois pode buscar por matrícula.
    """
    from inscricoes.models import Edital, Inscricao
    
    # Verifica se é assistente social, se for redireciona
    if hasattr(request.user, 'is_assistente_social') and request.user.is_assistente_social:
        return redirect('/dashboard/assistente/')
    
    matricula_search = None
    edital_selecionado = None
    inscricao_existente = None
    message = None
    
    # Verifica se deve limpar o edital selecionado (quando volta para seleção)
    if request.method == 'GET' and request.GET.get('clear_edital'):
        request.session.pop('edital_selecionado_id', None)
        edital_selecionado = None
        matricula_search = None  # Limpa também a matrícula pesquisada
    
    # Passo 1: Selecionar edital ativo (somente para visualização do estudante)
    editais_ativos = Edital.objects.filter(ativo=True, status='ATIVO')
    
    if request.method == 'POST':
        # Verifica se está limpando a seleção do edital
        if request.POST.get('clear_edital'):
            request.session.pop('edital_selecionado_id', None)
            edital_selecionado = None
        # Verifica se está selecionando um edital
        elif 'edital_id' in request.POST:
            edital_id = request.POST.get('edital_id')
            if edital_id:
                try:
                    edital_selecionado = Edital.objects.get(id=edital_id, ativo=True, status='ATIVO')
                    # Armazena o edital selecionado na sessão
                    request.session['edital_selecionado_id'] = edital_id
                    message = "Edital selecionado! Agora você pode buscar sua matrícula."
                except Edital.DoesNotExist:
                    message = "Edital não encontrado ou não está ativo."
        # Verifica se está buscando por matrícula
        elif 'matricula' in request.POST:
            matricula_search = request.POST.get('matricula', '').strip()
            
            # Obtém o edital selecionado da sessão
            edital_id = request.session.get('edital_selecionado_id')
            if edital_id:
                try:
                    edital_selecionado = Edital.objects.get(id=edital_id, ativo=True, status='ATIVO')
                except Edital.DoesNotExist:
                    edital_selecionado = None
            
            if matricula_search and edital_selecionado:
                # Buscar estudante pelo CPF (que é o username) e matrícula
                try:
                    estudante = Estudante.objects.get(cpf=request.user.username, matricula=matricula_search)
                    
                    # Verificar se já existe inscrição para este edital
                    inscricao_existente = Inscricao.objects.filter(
                        edital=edital_selecionado,
                        estudante=estudante
                    ).first()
                    
                    if inscricao_existente:
                        message = "Você já possui uma submissão para este edital."
                        # Redireciona para Step 3 (cards)
                        return redirect('step3_cards')
                    else:
                        message = "Matrícula encontrada! Preencha os dados abaixo para enviar sua submissão."
                        # Armazena dados do estudante na sessão para autopreenchimento
                        request.session['estudanteDados'] = {
                            'nome_completo': estudante.nome_completo,
                            'cpf': estudante.cpf,
                            'idade': estudante.idade,
                            'raca': estudante.raca,
                            'sexo': estudante.sexo,
                            'matricula': estudante.matricula,
                            'campus': estudante.campus,
                            'curso': estudante.curso,
                            'turno': estudante.turno,
                            'periodo': estudante.periodo,
                            'eh_cotista': estudante.eh_cotista,
                            'moradia_estudantil': estudante.moradia_estudantil,
                        }
                        # Se tiver endereço, armazena também
                        if hasattr(estudante, 'endereco') and estudante.endereco:
                            request.session['enderecoDados'] = {
                                'cep': estudante.endereco.cep,
                                'bairro': estudante.endereco.bairro,
                                'cidade': estudante.endereco.cidade,
                                'estado': estudante.endereco.estado,
                            }
                        # Redireciona para Step 3 (cards)
                        return redirect('step3_cards')
                        
                except Estudante.DoesNotExist:
                    message = "Matrícula não encontrada para o seu CPF."
            elif not edital_selecionado:
                message = "Por favor, selecione um edital ativo antes de buscar a matrícula."
    else:
        # Tenta carregar o edital selecionado da sessão
        edital_id = request.session.get('edital_selecionado_id')
        if edital_id:
            try:
                edital_selecionado = Edital.objects.get(id=edital_id, ativo=True, status='ATIVO')
            except Edital.DoesNotExist:
                # Se o edital não existe mais ou não está ativo, limpa a sessão
                request.session.pop('edital_selecionado_id', None)
                edital_selecionado = None
        
        # Se já tem edital selecionado, tenta carregar automaticamente a matrícula do estudante
        if edital_selecionado:
            try:
                estudante = Estudante.objects.get(cpf=request.user.username)
                matricula_search = estudante.matricula
                
                # Verificar se já existe inscrição
                inscricao_existente = Inscricao.objects.filter(
                    edital=edital_selecionado,
                    estudante=estudante
                ).first()
                
                if inscricao_existente:
                    message = "Você já possui uma submissão para este edital."
                else:
                    message = "Sua matrícula foi encontrada. Há um edital ativo disponível!"
            except Estudante.DoesNotExist:
                pass
    
    context = {
        'matricula_search': matricula_search,
        'edital': edital_selecionado,
        'editais_ativos': editais_ativos,
        'inscricao': inscricao_existente,
        'message': message,
    }
    
    return render(request, 'dashboard/student.html', context)


@login_required
def step3_cards_view(request):
    """
    View para Step 3 - Cards de navegação da jornada do estudante.
    Redireciona para o dashboard de enrollment correspondente.
    """
    from inscricoes.models import Edital
    
    # Obtém o edital selecionado da sessão
    edital_id = request.session.get('edital_selecionado_id')
    
    if not edital_id:
        messages.warning(request, 'Por favor, selecione um edital primeiro.')
        return redirect('student_dashboard')
    
    try:
        edital = Edital.objects.get(id=edital_id, ativo=True, status='ATIVO')
        # Redireciona para a URL de cards do enrollments usando o ID do edital como pk
        return redirect('enrollment_dashboard', pk=edital_id)
    except Edital.DoesNotExist:
        request.session.pop('edital_selecionado_id', None)
        messages.warning(request, 'Edital não encontrado ou não está mais ativo.')
        return redirect('student_dashboard')


@login_required
def assistente_edital_detalhes_view(request, edital_id):
    """
    View para mostrar detalhes de um edital específico com todas as submissões dos estudantes.
    Apenas usuários com is_assistente_social=True podem acessar.
    """
    # Verifica se o usuário é assistente social
    if not hasattr(request.user, 'is_assistente_social') or not request.user.is_assistente_social:
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
    Autopreenche os campos se houver dados na sessão (provenientes da busca por matrícula).
    """
    # Verifica se há dados na sessão para autopreenchimento
    initial_data = {}
    if hasattr(request.session, 'get'):
        estudante_dados = request.session.get('estudanteDados', {})
        endereco_dados = request.session.get('enderecoDados', {})
        
        # Mescla os dados do estudante e endereço
        if estudante_dados:
            initial_data.update(estudante_dados)
        if endereco_dados:
            initial_data.update(endereco_dados)
    
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
            
            # Limpar dados da sessão após salvar
            request.session.pop('estudanteDados', None)
            request.session.pop('enderecoDados', None)
            
            messages.success(request, 'Jornada concluída com sucesso! Seus dados foram salvos.')
            return redirect('buscar_cpf')
    else:
        # Usa dados iniciais da sessão se disponíveis
        form = JornadaForm(initial=initial_data if initial_data else None)
    
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
