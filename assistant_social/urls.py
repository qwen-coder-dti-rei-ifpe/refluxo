"""
URLs for Assistant Social (Social Worker) Dashboard
"""
from django.urls import path
from . import views

app_name = 'assistant_social'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Enrollment Analysis
    path('analise-inscricoes/', views.analise_inscricoes, name='analise_inscricoes'),
    path('inscricao/<int:pk>/', views.detalhe_inscricao, name='detalhe_inscricao'),
    
    # Appeal Analysis
    path('analise-recursos/', views.analise_recursos, name='analise_recursos'),
    path('recurso/<int:pk>/', views.detalhe_recurso, name='detalhe_recurso'),
    
    # Classification Management - Enrollments
    path('classificacao-inscricoes/', views.classificacao_inscricoes, name='classificacao_inscricoes'),
    path('gerenciar-classificacao-inscricao/<int:pk>/', views.gerenciar_classificacao_inscricao, name='gerenciar_classificacao_inscricao'),
    
    # Classification Management - Appeals
    path('classificacao-recursos/', views.classificacao_recursos, name='classificacao_recursos'),
    path('gerenciar-classificacao-recurso/<int:pk>/', views.gerenciar_classificacao_recurso, name='gerenciar_classificacao_recurso'),
]
