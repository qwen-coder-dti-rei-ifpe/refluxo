"""
URLs do aplicativo Students
"""
from django.urls import path
from . import views

urlpatterns = [
    # Busca de estudante (pública para consulta)
    path('search/', views.student_search, name='student_search'),
    
    # Listagem de estudantes
    path('', views.student_list, name='student_list'),
    
    # CRUD de estudantes
    path('create/', views.student_create, name='student_create'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/update/', views.student_update, name='student_update'),
]
