"""
Views para o Student Workspace - Espaço do Estudante
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from inscricoes.models import Edital, Inscricao
from core.models import Estudante


@login_required
def student_workspace_inicio(request):
    """
    Início - Lista todos os editais abertos
    """
    # Verifica se é assistente social
    if hasattr(request.user, 'is_assistente_social') and request.user.is_assistente_social:
        return redirect('/dashboard/assistente/')
    
    # Busca edital selecionado na sessão
    edital_id = request.session.get('edital_selecionado_id')
    
    # Lista todos os editais ABERTOS (status ATIVO e dentro do período de inscrição)
    now = timezone.now()
    editais_abertos = Edital.objects.filter(
        status='ATIVO',
        ativo=True,
        periodo_inscricao_abertura__lte=now,
        periodo_inscricao_fechamento__gte=now
    ).order_by('-criado_em')
    
    # Conta inscrições do estudante
    try:
        estudante = Estudante.objects.get(cpf=request.user.username)
        total_inscricoes = Inscricao.objects.filter(estudante=estudante).count()
        total_recursos = 0  # Implementar quando tiver modelo de Recurso
    except Estudante.DoesNotExist:
        total_inscricoes = 0
        total_recursos = 0
    
    context = {
        'editais_abertos': editais_abertos,
        'total_inscricoes': total_inscricoes,
        'total_recursos': total_recursos,
        'edital_selecionado_id': edital_id,
    }
    
    return render(request, 'student_workspace/inicio.html', context)


@login_required
def student_workspace_nova_inscricao(request):
    """
    Nova Inscrição - Formulário para nova inscrição em edital
    Filtros: edital no intervalo de tempo, situação aberta, estudante sem classificação
    """
    # Verifica se é assistente social
    if hasattr(request.user, 'is_assistente_social') and request.user.is_assistente_social:
        return redirect('/dashboard/assistente/')
    
    try:
        estudante = Estudante.objects.get(cpf=request.user.username)
    except Estudante.DoesNotExist:
        return redirect('student_workspace_inicio')
    
    now = timezone.now()
    
    # Editais elegíveis para nova inscrição:
    # - Status ATIVO e ativo=True
    # - Dentro do período de inscrição
    # - Estudante NÃO tem inscrição classificada neste edital
    editais_elegiveis = Edital.objects.filter(
        status='ATIVO',
        ativo=True,
        periodo_inscricao_abertura__lte=now,
        periodo_inscricao_fechamento__gte=now
    ).exclude(
        inscricao__estudante=estudante,
        inscricao__classificacao__in=['CONTEMPLADO', 'ELEGIVEL']
    ).distinct().order_by('titulo')
    
    if request.method == 'POST':
        edital_id = request.POST.get('edital_id')
        if edital_id:
            # Redireciona para o fluxo de inscrição
            request.session['edital_selecionado_id'] = edital_id
            return redirect('step3_cards')
    
    context = {
        'editais_elegiveis': editais_elegiveis,
        'total_inscricoes': Inscricao.objects.filter(estudante=estudante).count(),
        'total_recursos': 0,
    }
    
    return render(request, 'student_workspace/nova_inscricao.html', context)


@login_required
def student_workspace_minhas_inscricoes(request):
    """
    Minhas Inscrições - Lista todas as inscrições do estudante
    """
    # Verifica se é assistente social
    if hasattr(request.user, 'is_assistente_social') and request.user.is_assistente_social:
        return redirect('/dashboard/assistente/')
    
    try:
        estudante = Estudante.objects.get(cpf=request.user.username)
        inscricoes = Inscricao.objects.filter(
            estudante=estudante
        ).select_related('edital').order_by('-criado_em')
    except Estudante.DoesNotExist:
        inscricoes = Inscricao.objects.none()
    
    context = {
        'inscricoes': inscricoes,
        'total_inscricoes': inscricoes.count(),
        'total_recursos': 0,
    }
    
    return render(request, 'student_workspace/minhas_inscricoes.html', context)


@login_required
def student_workspace_novo_recurso(request):
    """
    Novo Recurso - Criar novo recurso sobre inscrição
    Filtros: inscrição submetida, analisada por assistente social,
    dentro do período de recurso, edital em período de recurso
    """
    # Verifica se é assistente social
    if hasattr(request.user, 'is_assistente_social') and request.user.is_assistente_social:
        return redirect('/dashboard/assistente/')
    
    try:
        estudante = Estudante.objects.get(cpf=request.user.username)
    except Estudante.DoesNotExist:
        return redirect('student_workspace_inicio')
    
    now = timezone.now()
    
    # Inscrições elegíveis para recurso:
    # - Inscrição SUBMETIDA e ANALISADA
    # - Edital em período de recurso
    inscricoes_elegiveis = Inscricao.objects.filter(
        estudante=estudante,
        status__in=['SUBMETIDA', 'EM_ANALISE', 'ANALISADA'],
        edital__status='ATIVO',
        edital__periodo_recurso_abertura__lte=now,
        edital__periodo_recurso_fechamento__gte=now
    ).select_related('edital').order_by('-submetida_em')
    
    if request.method == 'POST':
        inscricao_id = request.POST.get('inscricao_id')
        justificativa = request.POST.get('justificativa')
        
        if inscricao_id and justificativa:
            # TODO: Criar objeto Recurso quando o modelo estiver disponível
            # from inscricoes.models import Recurso
            # Recurso.objects.create(
            #     inscricao_id=inscricao_id,
            #     justificativa=justificativa,
            #     estudante=estudante
            # )
            return redirect('student_workspace_meus_recursos')
    
    context = {
        'inscricoes_elegiveis': inscricoes_elegiveis,
        'total_inscricoes': Inscricao.objects.filter(estudante=estudante).count(),
        'total_recursos': 0,
    }
    
    return render(request, 'student_workspace/novo_recurso.html', context)


@login_required
def student_workspace_meus_recursos(request):
    """
    Meus Recursos - Lista todos os recursos do estudante
    """
    # Verifica se é assistente social
    if hasattr(request.user, 'is_assistente_social') and request.user.is_assistente_social:
        return redirect('/dashboard/assistente/')
    
    try:
        estudante = Estudante.objects.get(cpf=request.user.username)
        # TODO: Implementar quando modelo Recurso estiver disponível
        # recursos = Recurso.objects.filter(estudante=estudante).order_by('-criado_em')
        recursos = []
    except Estudante.DoesNotExist:
        recursos = []
    
    context = {
        'recursos': recursos,
        'total_inscricoes': Inscricao.objects.filter(estudante=estudante).count() if estudante else 0,
        'total_recursos': len(recursos),
    }
    
    return render(request, 'student_workspace/meus_recursos.html', context)


@login_required
def student_workspace_avaliacoes(request):
    """
    Avaliações Integradas Conecta Gov - Página de integração
    """
    # Verifica se é assistente social
    if hasattr(request.user, 'is_assistente_social') and request.user.is_assistente_social:
        return redirect('/dashboard/assistente/')
    
    try:
        estudante = Estudante.objects.get(cpf=request.user.username)
    except Estudante.DoesNotExist:
        estudante = None
    
    context = {
        'estudante': estudante,
        'total_inscricoes': Inscricao.objects.filter(estudante=estudante).count() if estudante else 0,
        'total_recursos': 0,
    }
    
    return render(request, 'student_workspace/avaliacoes.html', context)
