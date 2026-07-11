"""
URLs do aplicativo Enrollments
"""
from django.urls import path
from . import views

urlpatterns = [
    # Listagem de editais para o pedagogo
    path('', views.enrollment_period_list, name='enrollment_period_list'),
    
    # Lista de estudantes inscritos para o pedagogo
    path('<int:pk>/students/', views.pedagogo_enrolled_students, name='pedagogo_enrolled_students'),
    
    # Dashboard de inscrição para um edital específico (estudante)
    path('<int:pk>/dashboard/', views.enrollment_dashboard, name='enrollment_dashboard'),
    
    # Criar/editar inscrição
    path('<int:pk>/create/', views.enrollment_create, name='enrollment_create'),
    path('<int:enrollment_pk>/update/', views.enrollment_update, name='enrollment_update'),
    
    # Submeter inscrição
    path('<int:enrollment_pk>/submit/', views.enrollment_submit, name='enrollment_submit'),
]
