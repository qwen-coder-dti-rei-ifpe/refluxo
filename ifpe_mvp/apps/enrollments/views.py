"""
Views do aplicativo Enrollments - Gestão de inscrições e editais
"""
import re
from datetime import datetime
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
        'student': student,
    }
    return render(request, 'enrollments/step3_cards.html', context)


@login_required
def step3_cards(request, pk):
    """Página de cards (Step 3) - Redireciona para o dashboard de cards."""
    return redirect('enrollment_dashboard', pk=pk)


@login_required
def store_matricula_search(request):
    """
    Endpoint AJAX para armazenar matrícula da busca na sessão e buscar dados do estudante.
    
    Fluxo:
    1. Recebe matrícula via POST
    2. Busca no banco de dados local
    3. Se não encontrar no banco, busca na API QAcadêmico
    4. Armazena dados na sessão
    5. Retorna JSON com sucesso ou erro
    """
    import json
    from django.http import JsonResponse
    from django.views.decorators.http import require_http_methods
    from integrations.qacademico_service import buscar_estudante_qacademico
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        matricula = data.get('matricula', '').strip()
        
        if not matricula:
            return JsonResponse({'success': False, 'error': 'Matrícula é obrigatória'})
        
        # Passo 1: Tentar buscar no banco de dados local
        try:
            student = Student.objects.get(matricula=matricula)
            
            # Dados encontrados no banco local
            dados_sessao = {
                'nome_completo': student.nome_completo or '',
                'cpf': student.cpf or '',
                'identidade': student.identidade or '',
                'data_nascimento': student.data_nascimento.strftime('%Y-%m-%d') if student.data_nascimento else '',
                'idade': student.idade or '',
                'raca': student.raca or '',
                'sexo': student.sexo or '',
                'genero': student.genero or student.sexo or '',
                'matricula': student.matricula or '',
                'campus': student.campus or '',
                'curso': student.curso or '',
                'turno': student.turno or '',
                'periodo': str(student.periodo) if student.periodo else '',
                'eh_cotista': student.eh_cotista,
                'email_pessoal': student.email_pessoal or '',
                'origem_escolar': student.origem_escolar or '',
                'moradia_estudantil': student.moradia_estudantil,
            }
            
            request.session['estudanteDados'] = dados_sessao
            request.session['student_data_loaded'] = False  # Resetar flag para recarregar do banco
            
            return JsonResponse({
                'success': True,
                'source': 'database',
                'message': 'Dados encontrados no banco de dados local',
                'data': dados_sessao
            })
            
        except Student.DoesNotExist:
            # Passo 2: Não encontrado no banco, buscar na API QAcadêmico
            dados_api, erro = buscar_estudante_qacademico(matricula)
            
            if dados_api:
                # Dados encontrados na API QAcadêmico
                request.session['estudanteDados'] = dados_api
                request.session['student_data_loaded'] = False  # Resetar flag para permitir carregamento
                
                return JsonResponse({
                    'success': True,
                    'source': 'qacademico_api',
                    'message': 'Dados encontrados na API QAcadêmico',
                    'data': dados_api
                })
            else:
                # Não encontrado nem no banco nem na API
                return JsonResponse({
                    'success': False,
                    'error': erro or 'Matrícula não encontrada no banco de dados ou na API QAcadêmico'
                })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dados inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'}, status=500)


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
    
    # Obter dados da sessão (provenientes da busca por matrícula via API QAcadêmico)
    estudante_dados = request.session.get('estudanteDados', {})
    
    # Flag para controlar se já carregou dados do banco na sessão
    already_loaded_from_db = request.session.get('student_data_loaded', False)
    
    # Lógica de preenchimento do formulário:
    # 1. Primeiro verifica se há dados da API QAcadêmico na sessão (busca recente por matrícula)
    # 2. Se não houver dados da API, carrega dados do banco local
    # 3. Dados da API têm prioridade sobre dados do banco
    
    if not already_loaded_from_db and student.id:
        # Carregar dados do banco para a sessão apenas uma vez
        db_data = {
            'nome_completo': student.nome_completo or '',
            'cpf': student.cpf or '',
            'identidade': student.identidade or '',
            'data_nascimento': student.data_nascimento.strftime('%Y-%m-%d') if student.data_nascimento else '',
            'idade': student.idade or '',
            'raca': student.raca or '',
            'sexo': student.sexo or '',
            'genero': student.genero or student.sexo or '',
            'matricula': student.matricula or '',
            'campus': student.campus or '',
            'curso': student.curso or '',
            'turno': student.turno or '',
            'periodo': str(student.periodo) if student.periodo else '',
            'eh_cotista': student.eh_cotista,
            'email_pessoal': student.email_pessoal or '',
            'origem_escolar': student.origem_escolar or '',
            'moradia_estudantil': student.moradia_estudantil,
            'tipo_conta': student.tipo_conta or '',
            'numero_agencia': student.numero_agencia or '',
            'numero_conta': student.numero_conta or '',
            'banco': student.banco or '',
            'banco_outro': student.banco_outro or '',
        }
        
        # Mesclar dados do banco com dados da API (API tem prioridade se existir)
        for key, value in db_data.items():
            if key not in estudante_dados or not estudante_dados[key]:
                estudante_dados[key] = value
        
        # Marcar que já carregou dados do banco
        request.session['student_data_loaded'] = True
        request.session['estudanteDados'] = estudante_dados
    
    # Atualizar campos específicos do student com dados da API QAcadêmico ANTES de renderizar
    if estudante_dados:
        # Mapear todos os campos necessários para o template
        if estudante_dados.get('nome_completo'):
            student.nome_completo = estudante_dados.get('nome_completo')
        if estudante_dados.get('cpf'):
            student.cpf = estudante_dados.get('cpf')
        if estudante_dados.get('identidade'):
            student.identidade = estudante_dados.get('identidade')
        if estudante_dados.get('data_nascimento'):
            student.data_nascimento = estudante_dados.get('data_nascimento')
            # Adiciona a versão formatada para exibição no template (DD/MM/YYYY)
            try:
                # Tenta parsear a data no formato YYYY-MM-DD
                date_obj = datetime.strptime(estudante_dados.get('data_nascimento'), '%Y-%m-%d')
                estudante_dados['data_nascimento_fmt'] = date_obj.strftime('%d/%m/%Y')
            except (ValueError, TypeError):
                # Se falhar, usa o valor original ou tenta outro formato
                estudante_dados['data_nascimento_fmt'] = estudante_dados.get('data_nascimento')
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
            # Extrair apenas o número do período (ex: "1º" -> 1)
            periodo_value = estudante_dados.get('periodo')
            if isinstance(periodo_value, str):
                match = re.match(r'(\d+)', periodo_value)
                if match:
                    student.periodo = int(match.group(1))
                else:
                    student.periodo = periodo_value
            else:
                student.periodo = periodo_value
        
        # Adicionar versão formatada do período para exibição no template
        if estudante_dados.get('periodo'):
            estudante_dados['periodo_fmt'] = estudante_dados.get('periodo')
        
        if estudante_dados.get('campus'):
            student.campus = estudante_dados.get('campus')
        if estudante_dados.get('curso'):
            student.curso = estudante_dados.get('curso')
        if estudante_dados.get('turno'):
            student.turno = estudante_dados.get('turno')
        if estudante_dados.get('eh_cotista') is not None:
            student.eh_cotista = estudante_dados.get('eh_cotista')
        if estudante_dados.get('matricula'):
            student.matricula = estudante_dados.get('matricula')
        
        # Email pessoal - mapear da API QAcademico
        if estudante_dados.get('email_pessoal'):
            student.email_pessoal = estudante_dados.get('email_pessoal')
        
        # Informações acadêmicas adicionais
        if estudante_dados.get('origem_escolar'):
            student.origem_escolar = estudante_dados.get('origem_escolar')
        if estudante_dados.get('moradia_estudantil') is not None:
            student.moradia_estudantil = estudante_dados.get('moradia_estudantil')
            
        # Garantir que genero esteja definido (fallback para sexo)
        if not hasattr(student, 'genero') or not student.genero:
            student.genero = estudante_dados.get('genero', estudante_dados.get('sexo', ''))
    
    if request.method == 'POST':
        # Salvar dados do estudante
        student = request.user.student
        student.nome_completo = request.POST.get('nome_completo', student.nome_completo)
        student.cpf = request.POST.get('cpf', student.cpf)
        student.identidade = request.POST.get('identidade', student.identidade)
        
        # Processar data de nascimento - converter de DD/MM/YYYY para YYYY-MM-DD
        data_nascimento_post = request.POST.get('data_nascimento', '')
        if data_nascimento_post:
            try:
                # Tentar parsear no formato DD/MM/YYYY
                date_obj = datetime.strptime(data_nascimento_post, '%d/%m/%Y')
                student.data_nascimento = date_obj.date()
            except ValueError:
                try:
                    # Tentar formato YYYY-MM-DD como fallback
                    date_obj = datetime.strptime(data_nascimento_post, '%Y-%m-%d')
                    student.data_nascimento = date_obj.date()
                except ValueError:
                    # Se falhar ambos, manter o valor atual ou limpar se vazio
                    if data_nascimento_post.strip():
                        messages.error(request, f'Formato de data inválido: {data_nascimento_post}. Use DD/MM/AAAA.')
                        context = {
                            'period': period,
                            'enrollment': enrollment,
                            'student': student,
                            'step': 4,
                            'total_steps': 8,
                            'estudante_dados': estudante_dados,
                        }
                        return render(request, 'enrollments/student_data_form.html', context)
                    else:
                        student.data_nascimento = None
        else:
            student.data_nascimento = None
        
        student.idade = request.POST.get('idade', student.idade)
        student.raca = request.POST.get('raca', student.raca)
        student.sexo = request.POST.get('sexo', student.sexo)
        student.genero = request.POST.get('genero', student.genero)
        student.orientacao_sexual = request.POST.get('orientacao_sexual', student.orientacao_sexual)
        
        # Processar período - extrair apenas o número se tiver sufixo ordinal
        periodo_post = request.POST.get('periodo', '')
        if periodo_post:
            match = re.match(r'(\d+)', periodo_post)
            if match:
                student.periodo = int(match.group(1))
            else:
                student.periodo = periodo_post
        
        student.campus = request.POST.get('campus', student.campus)
        student.curso = request.POST.get('curso', student.curso)
        student.turno = request.POST.get('turno', student.turno)
        
        # Processar quantidade de disciplinas - garantir que não seja negativo
        qtd_disciplinas = request.POST.get('quantidade_disciplinas', '0')
        try:
            qtd_value = int(qtd_disciplinas)
            student.quantidade_disciplinas = max(0, qtd_value)  # Garante valor não negativo
        except (ValueError, TypeError):
            student.quantidade_disciplinas = 0
        
        # Salvar origem escolar
        student.origem_escolar = request.POST.get('origem_escolar', student.origem_escolar)
        
        # Salvar moradia estudantil
        student.moradia_estudantil = request.POST.get('moradia_estudantil') == 'on'
        
        student.eh_cotista = request.POST.get('eh_cotista') == 'on'
        
        # Salvar emails
        student.email_institucional = request.POST.get('email_institucional', student.email_institucional)
        student.email_pessoal = request.POST.get('email_pessoal', student.email_pessoal)
        
        # Salvar informações bancárias
        student.tipo_conta = request.POST.get('tipo_conta', student.tipo_conta)
        student.numero_agencia = request.POST.get('numero_agencia', student.numero_agencia)
        student.numero_conta = request.POST.get('numero_conta', student.numero_conta)
        student.banco = request.POST.get('banco', student.banco)
        student.banco_outro = request.POST.get('banco_outro', student.banco_outro)
        
        student.save()
        
        # Limpar flags da sessão após salvar para permitir recarregamento na próxima visita
        request.session.pop('estudanteDados', None)
        request.session.pop('student_data_loaded', None)
        
        messages.success(request, 'Dados do estudante salvos com sucesso!')
        return redirect('address_data_form', pk=pk)
    
    # Garantir que student.data_nascimento_fmt e student.periodo_fmt estejam disponíveis no template
    if not estudante_dados.get('data_nascimento_fmt') and student.data_nascimento:
        estudante_dados['data_nascimento_fmt'] = student.data_nascimento.strftime('%d/%m/%Y')
    
    # Adicionar periodo_fmt se não existir na sessão mas o student tiver período
    if not estudante_dados.get('periodo_fmt') and student.periodo:
        estudante_dados['periodo_fmt'] = str(student.periodo) + 'º' if isinstance(student.periodo, int) else student.periodo
    
    context = {
        'period': period,
        'enrollment': enrollment,
        'student': student,
        'step': 4,
        'total_steps': 8,
        'estudante_dados': estudante_dados,  # Passar dados da API explicitamente para o template
        'form_data': estudante_dados,  # Alias para compatibilidade com o template
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
        student = enrollment.student
    
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
        'student': student,
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
        student = enrollment.student
    
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
        'student': student,
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
        student = enrollment.student
    
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
        'student': student,
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
        student = enrollment.student
    
    if request.method == 'POST':
        # Salvar dados de inscrição
        messages.success(request, 'Dados de inscrição salvos com sucesso!')
        return redirect('enrollment_dashboard', pk=pk)
    
    context = {
        'period': period,
        'enrollment': enrollment,
        'step': 8,
        'total_steps': 8,
        'student': student,
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
