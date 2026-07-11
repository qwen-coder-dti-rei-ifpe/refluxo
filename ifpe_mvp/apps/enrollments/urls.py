"""
URLs do aplicativo Enrollments
"""
from django.urls import path
from . import views

urlpatterns = [
    # Listagem de editais abertos
    path('', views.enrollment_period_list, name='enrollment_period_list'),
    
    # Dashboard de inscrição para um edital específico
    path('<int:pk>/', views.enrollment_dashboard, name='enrollment_dashboard'),
    
    # Criar/editar inscrição
    path('<int:pk>/create/', views.enrollment_create, name='enrollment_create'),
    path('<int:enrollment_pk>/update/', views.enrollment_update, name='enrollment_update'),
    
    # Submeter inscrição
    path('<int:enrollment_pk>/submit/', views.enrollment_submit, name='enrollment_submit'),
]
