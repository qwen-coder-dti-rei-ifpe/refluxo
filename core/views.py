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


# Importar serviço de integração com QAcadêmico
from integrations.qacademico_service import buscar_estudante_qacademico


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
    
    return render(request, 'core/assistente_social_dashboard.html', context)


@login_required
def student_dashboard_view(request):
    """
    View para dashboard do estudante.
    Primeiro o estudante deve selecionar um edital ativo, depois pode buscar por matrícula.
    Exibe card de Avaliação da Renda Familiar com dados do CadÚnico.
    Mostra também as inscrições realizadas pelo estudante.
    """
    from inscricoes.models import Edital, Inscricao
    from integrations.oauth_service import gerar_token_oauth
    from integrations.cadunico_service import buscar_dados_familiar, validar_cpf
    
    # Verifica se é assistente social, se for redireciona
    if hasattr(request.user, 'is_assistente_social') and request.user.is_assistente_social:
        return redirect('/dashboard/assistente/')
    
    matricula_search = None
    edital_selecionado = None
    inscricao_existente = None
    message = None
    dados_familiar = None
    erro_familiar = None
    faixa_renda_descricao = None
    
    # Buscar estudante logado
    estudante = None
    try:
        estudante = Estudante.objects.get(cpf=request.user.username)
    except Estudante.DoesNotExist:
        pass
    
    # Buscar todas as inscrições do estudante
    inscricoes = []
    if estudante:
        inscricoes = Inscricao.objects.filter(estudante=estudante).order_by('-criado_em')
    
    # Verifica se deve limpar o edital selecionado (quando volta para seleção)
    if request.method == 'GET' and request.GET.get('clear_edital'):
        request.session.pop('edital_selecionado_id', None)
        edital_selecionado = None
        matricula_search = None  # Limpa também a matrícula pesquisada
    
    # Passo 1: Selecionar edital ativo (somente para visualização do estudante)
    # Filtra apenas editais com status ATIVO e dentro do período de inscrições
    from django.utils import timezone
    agora = timezone.now()
    editais_ativos = Edital.objects.filter(
        ativo=True, 
        status='ATIVO',
        periodo_inscricao_abertura__lte=agora,
        periodo_inscricao_fechamento__gte=agora
    )
    
    # Buscar dados familiares do CadÚnico se tiver CPF do usuário
    cpf_usuario = request.user.username if hasattr(request.user, 'username') else None
    if cpf_usuario and validar_cpf(cpf_usuario):
        try:
            # Gerar token OAuth
            token, erro_token = gerar_token_oauth(cpf_usuario)
            
            if token and not erro_token:
                # Buscar dados familiares
                dados_familiar, erro_familiar = buscar_dados_familiar(cpf_usuario, token)
                
                if dados_familiar and not erro_familiar:
                    # Extrair descrição da faixa de renda per capita
                    faixa_renda = dados_familiar.get('faixaRendaFamiliarPerCapita', {})
                    if isinstance(faixa_renda, dict):
                        faixa_renda_descricao = faixa_renda.get('descricao', '')
                    elif isinstance(faixa_renda, list) and len(faixa_renda) > 0:
                        faixa_renda_descricao = faixa_renda[0].get('descricao', '') if isinstance(faixa_renda[0], dict) else ''
        except Exception as e:
            # Em caso de erro, apenas não exibe os dados (não quebra a página)
            pass
    
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
                # Primeiro, tentar buscar na API do QAcadêmico (Mock Postman)
                dados_qacademico, erro_api = buscar_estudante_qacademico(matricula_search)
                
                if dados_qacademico and not erro_api:
                    # Dados encontrados na API QAcadêmico - usar para preencher formulário
                    message = "Matrícula encontrada no QAcadêmico! Preencha os dados abaixo para enviar sua submissão."
                    
                    # Armazenar dados do estudante na sessão para autopreenchimento
                    request.session['estudanteDados'] = {
                        'nome_completo': dados_qacademico.get('nome_completo', ''),
                        'cpf': dados_qacademico.get('cpf', ''),
                        'identidade': dados_qacademico.get('identidade', ''),
                        'data_nascimento': dados_qacademico.get('data_nascimento', ''),
                        'idade': dados_qacademico.get('idade'),
                        'raca': dados_qacademico.get('raca', ''),
                        'sexo': dados_qacademico.get('sexo', ''),
                        'genero': dados_qacademico.get('sexo', ''),  # Gênero igual ao sexo por padrão
                        'matricula': dados_qacademico.get('matricula', ''),
                        'campus': dados_qacademico.get('campus', ''),
                        'curso': dados_qacademico.get('curso', ''),
                        'turno': dados_qacademico.get('turno', ''),
                        'periodo': dados_qacademico.get('periodo', ''),
                        'eh_cotista': dados_qacademico.get('eh_cotista', False),
                        'email_institucional': dados_qacademico.get('email_institucional', dados_qacademico.get('email', '')),
                        'email_pessoal': dados_qacademico.get('email_pessoal', dados_qacademico.get('email', '')),
                        'moradia_estudantil': False,
                    }
                    
                    # Redireciona para Step 3 (cards)
                    return redirect('step3_cards')
                
                # Se não encontrou na API, tenta buscar no banco local
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
                            'identidade': estudante.identidade if hasattr(estudante, 'identidade') else '',
                            'data_nascimento': str(estudante.data_nascimento) if hasattr(estudante, 'data_nascimento') and estudante.data_nascimento else '',
                            'idade': estudante.idade,
                            'raca': estudante.raca,
                            'sexo': estudante.sexo,
                            'genero': estudante.genero if hasattr(estudante, 'genero') else estudante.sexo,
                            'matricula': estudante.matricula,
                            'campus': estudante.campus,
                            'curso': estudante.curso,
                            'turno': estudante.turno,
                            'periodo': estudante.periodo,
                            'eh_cotista': estudante.eh_cotista,
                            'email_institucional': estudante.email_institucional if hasattr(estudante, 'email_institucional') else '',
                            'email_pessoal': estudante.email_pessoal if hasattr(estudante, 'email_pessoal') else '',
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
                    # Não encontrou nem na API nem no banco local
                    if erro_api:
                        message = f"Erro ao buscar matrícula: {erro_api}"
                    else:
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
        'dados_familiar': dados_familiar,
        'erro_familiar': erro_familiar,
        'faixa_renda_descricao': faixa_renda_descricao,
        'inscricoes': inscricoes,
        'estudante': estudante,
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
def avaliacoes_grid_view(request):
    """
    View para grid de avaliações do estudante.
    Exibe cards com resultados das avaliações, incluindo Avaliação da Renda Familiar.
    """
    from integrations.oauth_service import gerar_token_oauth
    from integrations.cadunico_service import buscar_dados_familiar, validar_cpf
    
    dados_familiar = None
    erro_familiar = None
    faixa_renda_descricao = None
    
    # Buscar dados familiares do CadÚnico se tiver CPF do usuário
    cpf_usuario = request.user.username if hasattr(request.user, 'username') else None
    
    if cpf_usuario and validar_cpf(cpf_usuario):
        try:
            # Gerar token OAuth
            token, erro_token = gerar_token_oauth(cpf_usuario)
            
            if token and not erro_token:
                # Buscar dados familiares
                dados_familiar, erro_familiar = buscar_dados_familiar(cpf_usuario, token)
                
                if dados_familiar and not erro_familiar:
                    # Extrair descrição da faixa de renda per capita
                    faixa_renda = dados_familiar.get('faixaRendaFamiliarPerCapita', {})
                    if isinstance(faixa_renda, dict):
                        faixa_renda_descricao = faixa_renda.get('descricao', '')
                    elif isinstance(faixa_renda, list) and len(faixa_renda) > 0:
                        faixa_renda_descricao = faixa_renda[0].get('descricao', '') if isinstance(faixa_renda[0], dict) else ''
        except Exception as e:
            # Em caso de erro, apenas não exibe os dados (não quebra a página)
            pass
    
    context = {
        'dados_familiar': dados_familiar,
        'erro_familiar': erro_familiar,
        'faixa_renda_descricao': faixa_renda_descricao,
    }
    
    return render(request, 'student/avaliacoes_grid.html', context)


@login_required
def resultado_avaliacao_renda_view(request):
    """
    View para página de resultado da avaliação da renda familiar.
    Exibe detalhes completos dos dados familiares do CadÚnico.
    """
    from integrations.oauth_service import gerar_token_oauth
    from integrations.cadunico_service import buscar_dados_familiar, validar_cpf
    
    dados_familiar = None
    erro_familiar = None
    faixa_renda_descricao = None
    
    # Buscar dados familiares do CadÚnico se tiver CPF do usuário
    cpf_usuario = request.user.username if hasattr(request.user, 'username') else None
    
    if cpf_usuario and validar_cpf(cpf_usuario):
        try:
            # Gerar token OAuth
            token, erro_token = gerar_token_oauth(cpf_usuario)
            
            if token and not erro_token:
                # Buscar dados familiares
                dados_familiar, erro_familiar = buscar_dados_familiar(cpf_usuario, token)
                
                if dados_familiar and not erro_familiar:
                    # Extrair descrição da faixa de renda per capita
                    faixa_renda = dados_familiar.get('faixaRendaFamiliarPerCapita', {})
                    if isinstance(faixa_renda, dict):
                        faixa_renda_descricao = faixa_renda.get('descricao', '')
                    elif isinstance(faixa_renda, list) and len(faixa_renda) > 0:
                        faixa_renda_descricao = faixa_renda[0].get('descricao', '') if isinstance(faixa_renda[0], dict) else ''
        except Exception as e:
            # Em caso de erro, apenas não exibe os dados (não quebra a página)
            erro_familiar = f"Erro ao buscar dados: {str(e)}"
    else:
        erro_familiar = "CPF inválido ou não informado"
    
    context = {
        'dados_familiar': dados_familiar,
        'erro_familiar': erro_familiar,
        'faixa_renda_descricao': faixa_renda_descricao,
    }
    
    return render(request, 'student/resultado_avaliacao_renda.html', context)


@login_required
def minhas_submissoes_view(request):
    """
    View para listar todas as submissões do estudante.
    Mostra inscrições em todos os editais que o estudante participou.
    """
    from ifpe_mvp.apps.enrollments.models import Enrollment, EnrollmentPeriod
    from core.models import Estudante
    
    try:
        estudante = Estudante.objects.get(cpf=request.user.username)
        # Tenta obter o Student do Django auth user primeiro
        try:
            student = request.user.student
            enrollments = Enrollment.objects.filter(student=student).select_related('enrollment_period').order_by('-criado_em')
        except:
            # Fallback para o modelo antigo se não encontrar Student
            enrollments = []
    except Estudante.DoesNotExist:
        enrollments = []
    
    context = {
        'inscricoes': enrollments,
        'is_enrollment_model': True,  # Flag para indicar que estamos usando o novo modelo
    }
    
    return render(request, 'student/minhas_submissoes.html', context)


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
    inscricoes = Inscricao.objects.filter(edital=edital).select_related('estudante').prefetch_related('familiares').order_by('-criado_em')
    
    context = {
        'edital': edital,
        'inscricoes': inscricoes,
    }
    
    return render(request, 'core/assistente_edital_detalhes.html', context)


@login_required
def assistente_novo_edital_view(request):
    """
    View para criar novo edital pelo assistente social.
    Redireciona para o admin do Django para criação do edital.
    """
    # Verifica se o usuário é assistente social
    if not hasattr(request.user, 'is_assistente_social') or not request.user.is_assistente_social:
        return render(request, 'core/sem_permissao.html')
    
    return redirect('/admin/inscricoes/edital/add/')


@login_required
def assistente_buscar_estudante_view(request):
    """
    View para buscar estudante por CPF ou matrícula pelo assistente social.
    Similar à busca do estudante, mas com contexto do assistente.
    """
    # Verifica se o usuário é assistente social
    if not hasattr(request.user, 'is_assistente_social') or not request.user.is_assistente_social:
        return render(request, 'core/sem_permissao.html')
    
    from core.models import Estudante
    from inscricoes.models import Inscricao
    
    search_query = None
    estudante_encontrado = None
    inscricoes_estudante = None
    message = None
    
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '').strip()
        
        if search_query:
            # Tenta buscar por CPF ou matrícula
            try:
                # Primeiro tenta buscar por CPF
                estudante_encontrado = Estudante.objects.get(cpf=search_query)
            except Estudante.DoesNotExist:
                try:
                    # Se não encontrar por CPF, tenta por matrícula
                    estudante_encontrado = Estudante.objects.get(matricula=search_query)
                except Estudante.DoesNotExist:
                    message = "Estudante não encontrado com o CPF ou matrícula informado."
            
            if estudante_encontrado:
                # Buscar todas as inscrições do estudante
                inscricoes_estudante = Inscricao.objects.filter(
                    estudante=estudante_encontrado
                ).select_related('edital').order_by('-criado_em')
                message = f"Estudante encontrado: {estudante_encontrado.nome_completo}"
    else:
        # GET - limpa a busca
        search_query = None
        estudante_encontrado = None
        inscricoes_estudante = None
    
    context = {
        'search_query': search_query,
        'estudante': estudante_encontrado,
        'inscricoes': inscricoes_estudante,
        'message': message,
    }
    
    return render(request, 'core/assistente_buscar_estudante.html', context)


@login_required
def assistente_analise_inscricao_view(request, edital_id=None):
    """
    View para análise de inscrições por edital pelo assistente social.
    Permite visualizar e avaliar as inscrições submetidas pelos estudantes.
    Apenas mostra inscrições dentro do período de submissão configurado no edital.
    """
    # Verifica se o usuário é assistente social
    if not hasattr(request.user, 'is_assistente_social') or not request.user.is_assistente_social:
        return render(request, 'core/sem_permissao.html')
    
    from inscricoes.models import Edital, Inscricao
    from django.utils import timezone
    
    edital_selecionado = None
    inscricoes = None
    fora_do_periodo = False
    
    if edital_id:
        edital_selecionado = get_object_or_404(Edital, pk=edital_id)
        
        # Verifica se está dentro do período de submissão de inscrições
        agora = timezone.now()
        if edital_selecionado.periodo_inscricao_abertura and edital_selecionado.periodo_inscricao_fechamento:
            if not (edital_selecionado.periodo_inscricao_abertura <= agora <= edital_selecionado.periodo_inscricao_fechamento):
                fora_do_periodo = True
        
        # Filtra inscrições do edital selecionado
        inscricoes = Inscricao.objects.filter(
            edital=edital_selecionado
        ).select_related('estudante').order_by('-criado_em')
    else:
        # Se não tem edital selecionado, mostra lista de editais para seleção
        pass
    
    # Lista todos os editais para seleção
    editais = Edital.objects.all().order_by('-criado_em')
    
    context = {
        'edital_selecionado': edital_selecionado,
        'inscricoes': inscricoes,
        'editais': editais,
        'fora_do_periodo': fora_do_periodo,
    }
    
    return render(request, 'core/assistente_analise_inscricao.html', context)


@login_required
def assistente_analise_recurso_view(request, edital_id=None):
    """
    View para análise de recursos por edital pelo assistente social.
    Permite visualizar e avaliar os recursos interpostos pelos estudantes.
    """
    # Verifica se o usuário é assistente social
    if not hasattr(request.user, 'is_assistente_social') or not request.user.is_assistente_social:
        return render(request, 'core/sem_permissao.html')
    
    from inscricoes.models import Edital, Inscricao, Recurso
    
    edital_selecionado = None
    recursos = None
    
    if edital_id:
        edital_selecionado = get_object_or_404(Edital, pk=edital_id)
        recursos = Recurso.objects.filter(
            inscricao__edital=edital_selecionado
        ).select_related('inscricao', 'inscricao__estudante').order_by('-criado_em')
    else:
        # Se não tem edital selecionado, mostra lista de editais para seleção
        pass
    
    # Lista todos os editais para seleção
    editais = Edital.objects.all().order_by('-criado_em')
    
    context = {
        'edital_selecionado': edital_selecionado,
        'recursos': recursos,
        'editais': editais,
    }
    
    return render(request, 'core/assistente_analise_recurso.html', context)


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
