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
    """
    form = StudentSearchForm(request.GET or None)
    student = None
    period_ativo = None
    
    if request.GET and form.is_valid():
        tipo_busca = form.cleaned_data['tipo_busca']
        valor_busca = form.cleaned_data['valor_busca']
        
        try:
            if tipo_busca == 'MATRICULA':
                student = Student.objects.get(matricula=valor_busca)
            elif tipo_busca == 'CPF':
                student = Student.objects.get(cpf=valor_busca)
            
            # Redireciona para a página de cards (Step 3) para continuar a inscrição
            # Primeiro precisamos encontrar o período de inscrição ativo
            from enrollments.models import EnrollmentPeriod
            from django.utils import timezone
            period_ativo = EnrollmentPeriod.objects.filter(
                ativo=True,
                data_fim__gte=timezone.now()
            ).order_by('-data_inicio').first()
            
            if period_ativo and student:
                # Redireciona diretamente para o Step 3 (cards)
                return redirect('enrollment_dashboard', pk=period_ativo.pk)
            elif not period_ativo:
                messages.info(request, 'Não há período de inscrição ativo no momento.')
                return redirect('dashboard')
        except Student.DoesNotExist:
            messages.warning(request, 'Estudante não encontrado. Realize o cadastro.')
            return redirect('student_create')
    
    context = {
        'form': form,
        'student': student,
        'period_ativo': period_ativo,
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
