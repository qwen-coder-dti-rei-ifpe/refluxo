"""
Views for Assistant Social (Social Worker) Dashboard
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from inscricoes.models import Edital, Inscricao as Enrollment
from core.models import Estudante as Student


# Try to import Appeal model if it exists
try:
    from inscricoes.models import Recurso as Appeal
except ImportError:
    Appeal = None


@login_required
def dashboard(request):
    """Main dashboard for assistant social"""
    campus = request.GET.get('campus', 'Recife')
    
    # Get counts for dashboard stats
    pending_enrollments = Enrollment.objects.filter(
        campus=campus,
        status='pending'
    ).count()
    
    pending_appeals = Appeal.objects.filter(
        enrollment__campus=campus,
        status='pending'
    ).count()
    
    analyzed_enrollments = Enrollment.objects.filter(
        campus=campus,
        status='analyzed'
    ).count()
    
    classified_count = Enrollment.objects.filter(
        campus=campus,
        is_classified=True
    ).count()
    
    # Recent enrollments for analysis
    recent_enrollments = Enrollment.objects.filter(
        campus=campus,
        status='pending'
    ).order_by('-created_at')[:5]
    
    context = {
        'pending_enrollments_count': pending_enrollments,
        'pending_appeals_count': pending_appeals,
        'analyzed_enrollments_count': analyzed_enrollments,
        'classified_count': classified_count,
        'recent_enrollments': recent_enrollments,
        'current_campus': campus,
    }
    
    return render(request, 'assistant_social/base.html', context)


@login_required
def analise_inscricoes(request):
    """List enrollments for analysis by edital"""
    campus = request.GET.get('campus', 'Recife')
    edital_id = request.GET.get('edital')
    
    enrollments = Enrollment.objects.filter(
        campus=campus,
        status='pending'
    ).select_related('student', 'edital').order_by('-created_at')
    
    if edital_id:
        enrollments = enrollments.filter(edital_id=edital_id)
    
    # Get all editais for filter dropdown
    editais = Edital.objects.filter(campus=campus).order_by('title')
    
    # Pagination
    paginator = Paginator(enrollments, 10)
    page_number = request.GET.get('page')
    enrollments_page = paginator.get_page(page_number)
    
    context = {
        'enrollments': enrollments_page,
        'editais': editais,
        'selected_edital': edital_id,
        'current_campus': campus,
        'pending_enrollments_count': Enrollment.objects.filter(campus=campus, status='pending').count(),
        'pending_appeals_count': Appeal.objects.filter(enrollment__campus=campus, status='pending').count(),
    }
    
    return render(request, 'assistant_social/analise_inscricoes.html', context)


@login_required
def analise_recursos(request):
    """List appeals for analysis by edital"""
    campus = request.GET.get('campus', 'Recife')
    edital_id = request.GET.get('edital')
    
    appeals = Appeal.objects.filter(
        enrollment__campus=campus,
        status='pending'
    ).select_related('enrollment__student', 'enrollment__edital').order_by('-created_at')
    
    if edital_id:
        appeals = appeals.filter(enrollment__edital_id=edital_id)
    
    # Get all editais for filter dropdown
    editais = Edital.objects.filter(campus=campus).order_by('title')
    
    # Pagination
    paginator = Paginator(appeals, 10)
    page_number = request.GET.get('page')
    appeals_page = paginator.get_page(page_number)
    
    context = {
        'appeals': appeals_page,
        'editais': editais,
        'selected_edital': edital_id,
        'current_campus': campus,
        'pending_enrollments_count': Enrollment.objects.filter(campus=campus, status='pending').count(),
        'pending_appeals_count': Appeal.objects.filter(enrollment__campus=campus, status='pending').count(),
    }
    
    return render(request, 'assistant_social/analise_recursos.html', context)


@login_required
def classificacao_inscricoes(request):
    """List analyzed enrollments for classification management"""
    campus = request.GET.get('campus', 'Recife')
    edital_id = request.GET.get('edital')
    
    enrollments = Enrollment.objects.filter(
        campus=campus,
        status='analyzed'
    ).select_related('student', 'edital').order_by('-analyzed_at')
    
    if edital_id:
        enrollments = enrollments.filter(edital_id=edital_id)
    
    # Get all editais for filter dropdown
    editais = Edital.objects.filter(campus=campus).order_by('title')
    
    # Pagination
    paginator = Paginator(enrollments, 10)
    page_number = request.GET.get('page')
    enrollments_page = paginator.get_page(page_number)
    
    context = {
        'enrollments': enrollments_page,
        'editais': editais,
        'selected_edital': edital_id,
        'current_campus': campus,
        'pending_enrollments_count': Enrollment.objects.filter(campus=campus, status='pending').count(),
        'pending_appeals_count': Appeal.objects.filter(enrollment__campus=campus, status='pending').count(),
    }
    
    return render(request, 'assistant_social/classificacao_inscricoes.html', context)


@login_required
def classificacao_recursos(request):
    """List analyzed appeals for classification management"""
    campus = request.GET.get('campus', 'Recife')
    edital_id = request.GET.get('edital')
    
    appeals = Appeal.objects.filter(
        enrollment__campus=campus,
        status='analyzed'
    ).select_related('enrollment__student', 'enrollment__edital').order_by('-analyzed_at')
    
    if edital_id:
        appeals = appeals.filter(enrollment__edital_id=edital_id)
    
    # Get all editais for filter dropdown
    editais = Edital.objects.filter(campus=campus).order_by('title')
    
    # Pagination
    paginator = Paginator(appeals, 10)
    page_number = request.GET.get('page')
    appeals_page = paginator.get_page(page_number)
    
    context = {
        'appeals': appeals_page,
        'editais': editais,
        'selected_edital': edital_id,
        'current_campus': campus,
        'pending_enrollments_count': Enrollment.objects.filter(campus=campus, status='pending').count(),
        'pending_appeals_count': Appeal.objects.filter(enrollment__campus=campus, status='pending').count(),
    }
    
    return render(request, 'assistant_social/classificacao_recursos.html', context)


@login_required
def detalhe_inscricao(request, pk):
    """Detail view of an enrollment for analysis"""
    enrollment = get_object_or_404(Enrollment, pk=pk)
    campus = request.GET.get('campus', enrollment.campus or 'Recife')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        score = request.POST.get('score')
        notes = request.POST.get('analysis_notes')
        
        if score:
            enrollment.score = float(score)
        enrollment.analysis_notes = notes
        
        if action == 'approve':
            enrollment.status = 'analyzed'
            enrollment.approved = True
        elif action == 'reject':
            enrollment.status = 'analyzed'
            enrollment.approved = False
        
        enrollment.analyzed_at = timezone.now()
        enrollment.save()
        
        return redirect('assistant_social:analise_inscricoes')
    
    context = {
        'enrollment': enrollment,
        'current_campus': campus,
        'pending_enrollments_count': Enrollment.objects.filter(campus=campus, status='pending').count(),
        'pending_appeals_count': Appeal.objects.filter(enrollment__campus=campus, status='pending').count(),
    }
    
    return render(request, 'assistant_social/detalhe_inscricao.html', context)


@login_required
def detalhe_recurso(request, pk):
    """Detail view of an appeal for analysis"""
    appeal = get_object_or_404(Appeal, pk=pk)
    campus = request.GET.get('campus', appeal.enrollment.campus or 'Recife')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('analysis_notes')
        new_score = request.POST.get('new_score')
        
        appeal.analysis_notes = notes
        
        if action == 'approve':
            appeal.is_approved = True
            appeal.is_rejected = False
            if new_score:
                appeal.enrollment.score = float(new_score)
                appeal.enrollment.save()
        elif action == 'reject':
            appeal.is_approved = False
            appeal.is_rejected = True
        
        appeal.status = 'analyzed'
        appeal.analyzed_at = timezone.now()
        appeal.save()
        
        return redirect('assistant_social:analise_recursos')
    
    context = {
        'appeal': appeal,
        'current_campus': campus,
        'pending_enrollments_count': Enrollment.objects.filter(campus=campus, status='pending').count(),
        'pending_appeals_count': Appeal.objects.filter(enrollment__campus=campus, status='pending').count(),
    }
    
    return render(request, 'assistant_social/detalhe_recurso.html', context)


@login_required
def gerenciar_classificacao_inscricao(request, pk):
    """Manage classification of an analyzed enrollment"""
    enrollment = get_object_or_404(Enrollment, pk=pk)
    campus = request.GET.get('campus', enrollment.campus or 'Recife')
    
    if request.method == 'POST':
        classification_status = request.POST.get('classification_status')
        classification_rank = request.POST.get('classification_rank')
        score = request.POST.get('score')
        notes = request.POST.get('notes')
        
        enrollment.is_classified = classification_status == 'classified'
        if classification_rank:
            enrollment.classification_rank = int(classification_rank)
        if score:
            enrollment.score = float(score)
        enrollment.classification_notes = notes
        enrollment.save()
        
        return redirect('assistant_social:classificacao_inscricoes')
    
    context = {
        'enrollment': enrollment,
        'current_campus': campus,
        'pending_enrollments_count': Enrollment.objects.filter(campus=campus, status='pending').count(),
        'pending_appeals_count': Appeal.objects.filter(enrollment__campus=campus, status='pending').count(),
    }
    
    return render(request, 'assistant_social/gerenciar_classificacao_inscricao.html', context)


@login_required
def gerenciar_classificacao_recurso(request, pk):
    """Manage classification of an analyzed appeal"""
    appeal = get_object_or_404(Appeal, pk=pk)
    campus = request.GET.get('campus', appeal.enrollment.campus or 'Recife')
    
    if request.method == 'POST':
        appeal_status = request.POST.get('appeal_status')
        new_score = request.POST.get('new_score')
        notes = request.POST.get('classification_notes')
        update_enrollment = request.POST.get('update_enrollment')
        
        appeal.is_approved = appeal_status == 'approved'
        appeal.is_rejected = appeal_status == 'rejected'
        appeal.classification_notes = notes
        
        if new_score and appeal.is_approved:
            appeal.enrollment.score = float(new_score)
            if update_enrollment:
                appeal.enrollment.save()
        
        appeal.save()
        
        return redirect('assistant_social:classificacao_recursos')
    
    context = {
        'appeal': appeal,
        'current_campus': campus,
        'pending_enrollments_count': Enrollment.objects.filter(campus=campus, status='pending').count(),
        'pending_appeals_count': Appeal.objects.filter(enrollment__campus=campus, status='pending').count(),
    }
    
    return render(request, 'assistant_social/gerenciar_classificacao_recurso.html', context)
