"""
URLs do aplicativo Enrollments
"""
from django.urls import path
from . import views

urlpatterns = [
    # Listagem de editais abertos
    path('', views.enrollment_period_list, name='enrollment_period_list'),
    
    # Dashboard de inscrição para um edital específico (Step 3 - Cards)
    path('<int:pk>/', views.enrollment_dashboard, name='enrollment_dashboard'),
    
    # URL alternativa para step3_cards (compatibilidade)
    path('<int:pk>/cards/', views.step3_cards, name='step3_cards'),
    
    # Step 4: Dados do Estudante
    path('<int:pk>/student-data/', views.student_data_form, name='student_data_form'),
    
    # Step 5: Dados de Endereço
    path('<int:pk>/address-data/', views.address_data_form, name='address_data_form'),
    
    # Step 6: Dados de Membros Familiares
    path('<int:pk>/family-members/', views.family_members_form, name='family_members_form'),
    
    # Step 7: Dados de Deslocamento
    path('<int:pk>/displacement-data/', views.displacement_data_form, name='displacement_data_form'),
    
    # Step 8: Dados de Inscrição
    path('<int:pk>/enrollment-data/', views.enrollment_data_form, name='enrollment_data_form'),
    
    # Criar/editar inscrição
    path('<int:pk>/create/', views.enrollment_create, name='enrollment_create'),
    path('<int:enrollment_pk>/update/', views.enrollment_update, name='enrollment_update'),
    
    # Submeter inscrição
    path('<int:enrollment_pk>/submit/', views.enrollment_submit, name='enrollment_submit'),
]
