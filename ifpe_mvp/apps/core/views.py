"""
Views do aplicativo Core - Páginas principais e autenticação
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    """Página inicial pública do sistema."""
    return render(request, 'core/home.html')


@login_required
def dashboard(request):
    """Dashboard principal do usuário autenticado."""
    context = {
        'user': request.user,
    }
    return render(request, 'core/dashboard.html', context)
