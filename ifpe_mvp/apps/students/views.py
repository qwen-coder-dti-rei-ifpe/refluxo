"""
Views do aplicativo Students - Visualização e edição de estudantes
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student
from .forms import StudentForm, StudentSearchForm


def student_search(request):
    """
    Página de busca de estudante por matrícula ou CPF.
    Permite consulta para autopreenchimento dos formulários.
    Integra com API QAcadêmico para buscar dados pela matrícula.
    """
    form = StudentSearchForm(request.GET or None)
    student = None
    period_ativo = None
    qacademico_data = None
    erro_api = None
    
    if request.GET and form.is_valid():
        tipo_busca = form.cleaned_data['tipo_busca']
        valor_busca = form.cleaned_data['valor_busca']
        
        # Se a busca for por matrícula, primeiro tenta buscar na API QAcadêmico
        if tipo_busca == 'MATRICULA':
            from integrations.qacademico_service import buscar_estudante_qacademico
            
            dados_api, erro = buscar_estudante_qacademico(valor_busca)
            
            if dados_api:
                # Dados encontrados na API QAcadêmico
                qacademico_data = dados_api
                
                # Tenta encontrar o estudante no banco local pela matrícula
                try:
                    student = Student.objects.get(matricula=valor_busca)
                except Student.DoesNotExist:
                    # Cria um novo estudante com os dados da API
                    student = Student(
                        matricula=dados_api.get('matricula', valor_busca),
                        nome_completo=dados_api.get('nome_completo', ''),
                        cpf=dados_api.get('cpf', ''),
                        identidade=dados_api.get('identidade', ''),
                        data_nascimento=dados_api.get('data_nascimento', None),
                        idade=dados_api.get('idade'),
                        raca=dados_api.get('raca', ''),
                        sexo=dados_api.get('sexo', ''),
                        campus=dados_api.get('campus', ''),
                        curso=dados_api.get('curso', ''),
                        turno=dados_api.get('turno', ''),
                        periodo=dados_api.get('periodo', ''),
                        eh_cotista=dados_api.get('eh_cotista', False),
                        email_institucional=dados_api.get('email', ''),
                    )
                    # Não salva ainda, apenas prepara para exibição
                
                # Armazena dados na sessão para pré-preenchimento do formulário
                # Mapeamento completo dos campos da API para o formulário
                dados_sessao = {
                    'nome_completo': dados_api.get('nome_completo', ''),
                    'cpf': dados_api.get('cpf', ''),
                    'identidade': dados_api.get('identidade', ''),  # brRG
                    'data_nascimento': dados_api.get('data_nascimento', ''),  # birthday
                    'idade': dados_api.get('idade', ''),
                    'raca': dados_api.get('raca', ''),
                    'sexo': dados_api.get('sexo', ''),  # gender (M/F -> MASCULINO/FEMININO)
                    'genero': dados_api.get('sexo', ''),  # Gênero igual ao sexo para pré-preenchimento
                    'matricula': dados_api.get('matricula', ''),
                    'campus': dados_api.get('campus', ''),
                    'curso': dados_api.get('curso', ''),
                    'turno': dados_api.get('turno', ''),
                    'periodo': dados_api.get('periodo', ''),  # currentPeriod formatado como "1º"
                    'eh_cotista': dados_api.get('eh_cotista', False),
                    'email_pessoal': dados_api.get('email', ''),  # Email Pessoal (campo email da API)
                    'email_institucional': '',  # Email Institucional (separado do email pessoal)
                    'nome_mae': dados_api.get('nome_mae', ''),
                    'nome_pai': dados_api.get('nome_pai', ''),
                    'estado_civil': dados_api.get('estado_civil', ''),
                    'numero_filhos': dados_api.get('numero_filhos', 0),
                    'status_matricula': dados_api.get('status_matricula', ''),
                    'nivel_curso': dados_api.get('nivel_curso', ''),
                    'media_geral': dados_api.get('media_geral', 0.0),
                }
                request.session['estudanteDados'] = dados_sessao
                
                messages.success(request, f'Dados encontrados na API QAcadêmico para matrícula {valor_busca}')
                
            elif erro:
                # Erro ou não encontrado na API, busca apenas no banco local
                erro_api = erro
                try:
                    student = Student.objects.get(matricula=valor_busca)
                    messages.info(request, 'Dados buscados apenas na base local.')
                except Student.DoesNotExist:
                    messages.warning(request, f'Estudante não encontrado. {erro}')
                    return redirect('student_create')
        
        # Se a busca for por CPF ou se não encontrou na API, busca no banco local
        if tipo_busca == 'CPF' or (tipo_busca == 'MATRICULA' and not qacademico_data):
            try:
                if tipo_busca == 'CPF':
                    student = Student.objects.get(cpf=valor_busca)
                elif tipo_busca == 'MATRICULA' and not student:
                    student = Student.objects.get(matricula=valor_busca)
                
                messages.info(request, 'Dados buscados na base local.')
            except Student.DoesNotExist:
                if not erro_api:
                    messages.warning(request, 'Estudante não encontrado. Realize o cadastro.')
                return redirect('student_create')
        
        # Redireciona para a página de cards (Step 3) para continuar a inscrição
        # Primeiro precisamos encontrar o período de inscrição ativo
        from enrollments.models import EnrollmentPeriod
        from django.utils import timezone
        period_ativo = EnrollmentPeriod.objects.filter(
            ativo=True,
            data_fim__gte=timezone.now()
        ).order_by('-data_inicio').first()
        
        if period_ativo and (student or qacademico_data):
            # Redireciona diretamente para o Step 3 (cards)
            # Os dados da sessão serão usados para pré-preencher o formulário
            return redirect('enrollment_dashboard', pk=period_ativo.pk)
        elif not period_ativo:
            messages.info(request, 'Não há período de inscrição ativo no momento.')
            return redirect('dashboard')
    
    context = {
        'form': form,
        'student': student,
        'period_ativo': period_ativo,
        'qacademico_data': qacademico_data,
        'erro_api': erro_api,
    }
    return render(request, 'students/student_search.html', context)


@login_required
def student_list(request):
    """Lista todos os estudantes cadastrados."""
    students = Student.objects.all().order_by('nome_completo')
    context = {'students': students}
    return render(request, 'students/student_list.html', context)


@login_required
def student_detail(request, pk):
    """Detalhes de um estudante específico."""
    student = get_object_or_404(Student, pk=pk)
    context = {'student': student}
    return render(request, 'students/student_detail.html', context)


@login_required
def student_create(request):
    """Cadastro de novo estudante."""
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, 'Estudante cadastrado com sucesso!')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm()
    
    context = {'form': form}
    return render(request, 'students/student_form.html', context)


@login_required
def student_update(request, pk):
    """Edição de estudante existente."""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    
    context = {'form': form, 'student': student}
    return render(request, 'students/student_form.html', context)
