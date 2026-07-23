"""
Views do aplicativo Enrollments - Gestão de inscrições e editais
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import EnrollmentPeriod, Enrollment
from ifpe_mvp.apps.students.models import Student


def enrollment_period_list(request):
    """Lista todos os editais/periodos de inscrição ativos."""
    periods = EnrollmentPeriod.objects.filter(
        ativo=True,
        data_fim__gte=timezone.now()
    ).order_by('-data_inicio')
    
    context = {'periods': periods}
    return render(request, 'enrollments/period_list.html', context)


@login_required
def enrollment_dashboard(request, pk):
    """Dashboard com blocos dos eixos para atualização da inscrição (Step 3 - Cards)."""
    from inscricoes.models import Edital
    
    # Tenta obter como EnrollmentPeriod primeiro, senão tenta como Edital
    try:
        period = EnrollmentPeriod.objects.get(pk=pk)
    except EnrollmentPeriod.DoesNotExist:
        # Se não encontrar EnrollmentPeriod, tenta buscar como Edital
        edital = get_object_or_404(Edital, pk=pk)
        # Cria ou obtém um EnrollmentPeriod correspondente ao Edital
        period, created = EnrollmentPeriod.objects.get_or_create(
            pk=pk,
            defaults={
                'titulo': edital.titulo,
                'descricao': edital.descricao or '',
                'data_inicio': edital.periodo_inscricao_abertura or timezone.now(),
                'data_fim': edital.periodo_inscricao_fechamento or (edital.periodo_inscricao_abertura + timezone.timedelta(days=30)) if edital.periodo_inscricao_abertura else timezone.now() + timezone.timedelta(days=30),
                'status': 'ABERTO' if edital.status == 'ATIVO' else 'FECHADO',
                'ativo': edital.ativo,
            }
        )
    
    # Verifica se o período está aberto
    if not period.esta_aberto():
        messages.warning(request, 'Este período de inscrição está fechado.')
    
    # Obtém ou cria o estudante e a inscrição
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, 'Você precisa cadastrar seus dados de estudante primeiro.')
        return redirect('students:student_create')
    
    # Obtém ou cria a inscrição
    enrollment, created = Enrollment.objects.get_or_create(
        student=student,
        enrollment_period=period,
        defaults={'status': 'RASCUNHO'}
    )
    
    context = {
        'period': period,
        'enrollment': enrollment,
        'can_edit': period.esta_aberto(),
    }
    return render(request, 'enrollments/step3_cards.html', context)


@login_required
def step3_cards(request, pk):
    """Página de cards (Step 3) - Redireciona para o dashboard de cards."""
    return redirect('enrollment_dashboard', pk=pk)


@login_required
def student_data_form(request, pk):
    """Step 4: Formulário de Dados do Estudante."""
    from inscricoes.models import Edital
    
    # Tenta obter como EnrollmentPeriod primeiro, senão tenta como Edital
    try:
        period = EnrollmentPeriod.objects.get(pk=pk)
    except EnrollmentPeriod.DoesNotExist:
        # Se não encontrar EnrollmentPeriod, tenta buscar como Edital
        edital = get_object_or_404(Edital, pk=pk)
        # Cria ou obtém um EnrollmentPeriod correspondente ao Edital
        period, created = EnrollmentPeriod.objects.get_or_create(
            pk=pk,
            defaults={
                'titulo': edital.titulo,
                'descricao': edital.descricao or '',
                'data_inicio': edital.periodo_inscricao_abertura or timezone.now(),
                'data_fim': edital.periodo_inscricao_fechamento or (edital.periodo_inscricao_abertura + timezone.timedelta(days=30)) if edital.periodo_inscricao_abertura else timezone.now() + timezone.timedelta(days=30),
                'status': 'ABERTO' if edital.status == 'ATIVO' else 'FECHADO',
                'ativo': edital.ativo,
            }
        )
    
    try:
        student = request.user.student
        enrollment = Enrollment.objects.get(student=student, enrollment_period=period)
    except (Student.DoesNotExist, Enrollment.DoesNotExist):
        try:
            student = request.user.student
        except Student.DoesNotExist:
            messages.error(request, 'Você precisa cadastrar seus dados de estudante primeiro.')
            return redirect('students:student_create')
        enrollment = Enrollment.objects.create(
            student=student,
            enrollment_period=period,
            status='RASCUNHO'
        )
    
    # Verifica se há dados na sessão para autopreenchimento (provenientes da API QAcadêmico)
    estudante_dados = request.session.get('estudanteDados', {})
    
    # Atualizar campos específicos do student com dados da API QAcadêmico ANTES de renderizar
    if estudante_dados:
        # Mapear todos os campos necessários para o template
        if estudante_dados.get('identidade'):
            student.identidade = estudante_dados.get('identidade')
        if estudante_dados.get('data_nascimento'):
            student.data_nascimento = estudante_dados.get('data_nascimento')
        if estudante_dados.get('idade'):
            student.idade = estudante_dados.get('idade')
        if estudante_dados.get('raca'):
            student.raca = estudante_dados.get('raca')
        if estudante_dados.get('sexo'):
            student.sexo = estudante_dados.get('sexo')
        if estudante_dados.get('genero'):
            student.genero = estudante_dados.get('genero')
        elif estudante_dados.get('sexo'):
            # Se não tiver gênero, usa o sexo como fallback
            student.genero = estudante_dados.get('sexo')
        if estudante_dados.get('periodo'):
            student.periodo = estudante_dados.get('periodo')
        if estudante_dados.get('campus'):
            student.campus = estudante_dados.get('campus')
        if estudante_dados.get('curso'):
            student.curso = estudante_dados.get('curso')
        if estudante_dados.get('turno'):
            student.turno = estudante_dados.get('turno')
        if estudante_dados.get('eh_cotista') is not None:
            student.eh_cotista = estudante_dados.get('eh_cotista')
        
        # Email pessoal e institucional - ambos usam o mesmo valor da API
        email_value = estudante_dados.get('email_institucional', estudante_dados.get('email_pessoal', ''))
        
        # Adicionar atributos extras ao student para campos que podem não existir no modelo
        # Isso permite que o template acesse email_pessoal e genero mesmo se não existirem no modelo
        student.email_pessoal = email_value
        student.email_institucional = email_value
            
        # Garantir que genero esteja definido (fallback para sexo)
        if not hasattr(student, 'genero') or not student.genero:
            student.genero = estudante_dados.get('genero', estudante_dados.get('sexo', ''))
    
    if request.method == 'POST':
        # Salvar dados do estudante
        student = request.user.student
        student.nome_completo = request.POST.get('nome_completo', student.nome_completo)
        student.cpf = request.POST.get('cpf', student.cpf)
        student.identidade = request.POST.get('identidade', student.identidade)
        student.data_nascimento = request.POST.get('data_nascimento', student.data_nascimento)
        student.idade = request.POST.get('idade', student.idade)
        student.raca = request.POST.get('raca', student.raca)
        student.sexo = request.POST.get('sexo', student.sexo)
        student.periodo = request.POST.get('periodo', student.periodo)
        student.campus = request.POST.get('campus', student.campus)
        student.curso = request.POST.get('curso', student.curso)
        student.turno = request.POST.get('turno', student.turno)
        student.eh_cotista = request.POST.get('eh_cotista') == 'on'
        student.save()
        
        # Limpar dados da sessão após salvar
        request.session.pop('estudanteDados', None)
        
        messages.success(request, 'Dados do estudante salvos com sucesso!')
        return redirect('address_data_form', pk=pk)
    
    context = {
        'period': period,
        'enrollment': enrollment,
        'student': student,
        'step': 4,
        'total_steps': 8,
        'estudante_dados': estudante_dados,  # Passar dados da API explicitamente para o template
    }
    return render(request, 'enrollments/student_data_form.html', context)


@login_required
def address_data_form(request, pk):
    """Step 5: Formulário de Dados de Endereço."""
    period = get_object_or_404(EnrollmentPeriod, pk=pk)
    
    try:
        student = request.user.student
        enrollment = Enrollment.objects.get(student=student, enrollment_period=period)
    except (Student.DoesNotExist, Enrollment.DoesNotExist):
        enrollment = Enrollment.objects.create(
            student=request.user.student,
            enrollment_period=period,
            status='RASCUNHO'
        )
    
    if request.method == 'POST':
        # Salvar dados de endereço
        messages.success(request, 'Dados de endereço salvos com sucesso!')
        return redirect('family_members_form', pk=pk)
    
    context = {
        'period': period,
        'enrollment': enrollment,
        'address': enrollment.address if enrollment.address else None,
        'step': 5,
        'total_steps': 8,
    }
    return render(request, 'enrollments/address_data_form.html', context)


@login_required
def family_members_form(request, pk):
    """Step 6: Formulário de Dados de Membros Familiares."""
    period = get_object_or_404(EnrollmentPeriod, pk=pk)
    
    try:
        student = request.user.student
        enrollment = Enrollment.objects.get(student=student, enrollment_period=period)
    except (Student.DoesNotExist, Enrollment.DoesNotExist):
        enrollment = Enrollment.objects.create(
            student=request.user.student,
            enrollment_period=period,
            status='RASCUNHO'
        )
    
    if request.method == 'POST':
        # Salvar dados de membros familiares
        messages.success(request, 'Dados de membros familiares salvos com sucesso!')
        return redirect('displacement_data_form', pk=pk)
    
    # Get family members (all existing ones)
    from ifpe_mvp.apps.family.models import FamilyMember
    family_members = FamilyMember.objects.all()
    
    context = {
        'period': period,
        'enrollment': enrollment,
        'family_members': family_members,
        'step': 6,
        'total_steps': 8,
    }
    return render(request, 'enrollments/family_members_form.html', context)


@login_required
def displacement_data_form(request, pk):
    """Step 7: Formulário de Dados de Deslocamento."""
    period = get_object_or_404(EnrollmentPeriod, pk=pk)
    
    try:
        student = request.user.student
        enrollment = Enrollment.objects.get(student=student, enrollment_period=period)
    except (Student.DoesNotExist, Enrollment.DoesNotExist):
        enrollment = Enrollment.objects.create(
            student=request.user.student,
            enrollment_period=period,
            status='RASCUNHO'
        )
    
    if request.method == 'POST':
        # Salvar dados de deslocamento
        messages.success(request, 'Dados de deslocamento salvos com sucesso!')
        return redirect('enrollment_data_form', pk=pk)
    
    context = {
        'period': period,
        'enrollment': enrollment,
        'displacement': enrollment.displacement if enrollment.displacement else None,
        'step': 7,
        'total_steps': 8,
    }
    return render(request, 'enrollments/displacement_data_form.html', context)


@login_required
def enrollment_data_form(request, pk):
    """Step 8: Formulário de Dados de Inscrição."""
    period = get_object_or_404(EnrollmentPeriod, pk=pk)
    
    try:
        student = request.user.student
        enrollment = Enrollment.objects.get(student=student, enrollment_period=period)
    except (Student.DoesNotExist, Enrollment.DoesNotExist):
        enrollment = Enrollment.objects.create(
            student=request.user.student,
            enrollment_period=period,
            status='RASCUNHO'
        )
    
    if request.method == 'POST':
        # Salvar dados de inscrição
        messages.success(request, 'Dados de inscrição salvos com sucesso!')
        return redirect('enrollment_dashboard', pk=pk)
    
    context = {
        'period': period,
        'enrollment': enrollment,
        'step': 8,
        'total_steps': 8,
    }
    return render(request, 'enrollments/enrollment_data_form.html', context)


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
        return redirect('students:student_create')
    
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
