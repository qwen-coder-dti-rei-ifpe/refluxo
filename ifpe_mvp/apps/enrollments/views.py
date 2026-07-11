"""
Views do aplicativo Enrollments - Gestão de inscrições e editais
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import EnrollmentPeriod, Enrollment
from students.models import Student


def enrollment_period_list(request):
    """Lista todos os editais/periodos de inscrição para o pedagogo."""
    # Filtros da requisição
    nome_filter = request.GET.get('nome', '')
    status_filter = request.GET.get('status', '')
    
    periods = EnrollmentPeriod.objects.all().order_by('-data_inicio')
    
    # Aplicar filtros
    if nome_filter:
        periods = periods.filter(Q(titulo__icontains=nome_filter) | Q(descricao__icontains=nome_filter))
    
    if status_filter:
        periods = periods.filter(status=status_filter)
    
    # Adicionar quantidade de inscritos
    for period in periods:
        period.qtd_inscritos = period.enrollments.count()
    
    context = {
        'periods': periods,
        'nome_filter': nome_filter,
        'status_filter': status_filter,
        'status_choices': EnrollmentPeriod.STATUS_CHOICES,
    }
    return render(request, 'enrollments/period_list_pedagogo.html', context)


@login_required
def pedagogo_enrolled_students(request, pk):
    """Lista de estudantes inscritos em um edital específico para o pedagogo."""
    period = get_object_or_404(EnrollmentPeriod, pk=pk)
    
    # Filtros da requisição
    nome_filter = request.GET.get('nome', '')
    curso_filter = request.GET.get('curso', '')
    modalidade_filter = request.GET.get('modalidade', '')
    ivs_filter = request.GET.get('ivs', '')
    situacao_filter = request.GET.get('situacao', '')
    
    enrollments = Enrollment.objects.filter(enrollment_period=period).select_related('student').order_by('student__nome_completo')
    
    # Aplicar filtros
    if nome_filter:
        enrollments = enrollments.filter(student__nome_completo__icontains=nome_filter)
    
    if curso_filter:
        enrollments = enrollments.filter(student__curso__icontains=curso_filter)
    
    if modalidade_filter:
        # Considerando que modalidade pode estar no curso ou em outro campo
        enrollments = enrollments.filter(Q(student__curso__icontains=modalidade_filter))
    
    if ivs_filter:
        try:
            ivs_value = float(ivs_filter.replace(',', '.'))
            enrollments = enrollments.filter(indice_vulnerabilidade__gte=ivs_value)
        except ValueError:
            pass
    
    if situacao_filter:
        enrollments = enrollments.filter(status=situacao_filter)
    
    context = {
        'period': period,
        'enrollments': enrollments,
        'nome_filter': nome_filter,
        'curso_filter': curso_filter,
        'modalidade_filter': modalidade_filter,
        'ivs_filter': ivs_filter,
        'situacao_filter': situacao_filter,
        'situacao_choices': Enrollment.STATUS_CHOICES,
    }
    return render(request, 'enrollments/pedagogo_enrolled_students.html', context)


@login_required
def enrollment_dashboard(request, pk):
    """Dashboard com blocos dos eixos para atualização da inscrição."""
    period = get_object_or_404(EnrollmentPeriod, pk=pk)
    
    # Verifica se o período está aberto
    if not period.esta_aberto():
        messages.warning(request, 'Este período de inscrição está fechado.')
    
    # Tenta obter a inscrição existente do usuário
    try:
        student = request.user.student
        enrollment = Enrollment.objects.get(student=student, enrollment_period=period)
    except (Student.DoesNotExist, Enrollment.DoesNotExist):
        enrollment = None
    
    context = {
        'period': period,
        'enrollment': enrollment,
        'can_edit': period.esta_aberto(),
    }
    return render(request, 'enrollments/enrollment_dashboard.html', context)


@login_required
def enrollment_create(request, pk):
    """Cria uma nova inscrição para um período específico."""
    period = get_object_or_404(EnrollmentPeriod, pk=pk)
    
    if not period.esta_aberto():
        messages.error(request, 'Não é possível criar inscrição fora do período.')
        return redirect('enrollment_period_list')
    
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Você precisa cadastrar seus dados de estudante primeiro.')
        return redirect('student_create')
    
    # Cria inscrição vazia
    enrollment = Enrollment.objects.create(
        student=student,
        enrollment_period=period,
        status='RASCUNHO'
    )
    
    messages.success(request, 'Inscrição criada. Preencha as informações.')
    return redirect('enrollment_update', enrollment_pk=enrollment.pk)


@login_required
def enrollment_update(request, enrollment_pk):
    """Atualiza uma inscrição existente."""
    enrollment = get_object_or_404(Enrollment, pk=enrollment_pk)
    
    # Verifica se pode editar
    if not enrollment.pode_editar():
        messages.error(request, 'Esta inscrição não pode mais ser editada.')
        return redirect('enrollment_dashboard', pk=enrollment.enrollment_period.pk)
    
    if request.method == 'POST':
        # Atualização simplificada - em produção usaria forms específicos
        enrollment.renda_bruta_familiar = request.POST.get('renda_bruta_familiar', 0)
        enrollment.renda_per_capita = request.POST.get('renda_per_capita', 0)
        enrollment.declaracao_veracidade = request.POST.get('declaracao_veracidade') == 'on'
        enrollment.save()
        
        messages.success(request, 'Inscrição atualizada com sucesso!')
        return redirect('enrollment_dashboard', pk=enrollment.enrollment_period.pk)
    
    context = {'enrollment': enrollment}
    return render(request, 'enrollments/enrollment_form.html', context)


@login_required
def enrollment_submit(request, enrollment_pk):
    """Submete a inscrição para análise."""
    enrollment = get_object_or_404(Enrollment, pk=enrollment_pk)
    
    # Verifica se pode submeter
    if not enrollment.pode_editar():
        messages.error(request, 'Esta inscrição não pode ser submetida.')
        return redirect('enrollment_dashboard', pk=enrollment.enrollment_period.pk)
    
    if request.method == 'POST':
        enrollment.submeter()
        messages.success(request, 'Inscrição submetida com sucesso para análise!')
        return redirect('enrollment_dashboard', pk=enrollment.enrollment_period.pk)
    
    context = {'enrollment': enrollment}
    return render(request, 'enrollments/enrollment_submit.html', context)
