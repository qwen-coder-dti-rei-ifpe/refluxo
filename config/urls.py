"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core.views import home_view, buscar_cpf_view, CustomLoginView, assistente_dashboard_view, assistente_edital_detalhes_view, jornada_estudante_view, student_dashboard_view, step3_cards_view, avaliacoes_grid_view, minhas_submissoes_view

urlpatterns = [
    # Página inicial do programa
    path('', home_view, name='home'),
    
    # Busca de estudante por CPF
    path('buscar-cpf/', buscar_cpf_view, name='buscar_cpf'),
    
    # Login personalizado com autopreenchimento
    path('login/', CustomLoginView.as_view(), name='login'),
    
    # Logout
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    
    # Dashboard do Estudante (substitui jornada-estudante como destino pós-login)
    path('dashboard/student/', student_dashboard_view, name='student_dashboard'),
    
    # Jornada do Estudante (fluxo de preenchimento completo)
    path('jornada-estudante/', jornada_estudante_view, name='jornada_estudante'),
    
    # Step 3 - Cards de navegação da jornada
    path('step3-cards/', step3_cards_view, name='step3_cards'),
    
    # Avaliações Grid - Página de cards de avaliações
    path('avaliacoes/', avaliacoes_grid_view, name='avaliacoes_grid'),
    
    # Minhas Submissões - Lista de todas as submissões do estudante
    path('minhas-submissoes/', minhas_submissoes_view, name='minhas_submissoes'),
    
    # Enrollment app URLs (fluxo de inscrição completo)
    path('enrollments/', include('ifpe_mvp.apps.enrollments.urls')),
    
    # Students app URLs
    path('students/', include('ifpe_mvp.apps.students.urls', namespace='students')),

    # Family app URLs
    path('family/', include('ifpe_mvp.apps.family.urls')),
    # Área do Assistente Social
    path('dashboard/assistente/', assistente_dashboard_view, name='assistente_dashboard'),
    path('assistente/edital/<int:edital_id>/', assistente_edital_detalhes_view, name='assistente_edital_detalhes'),
    
    # Admin Django
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/core/', include('core.urls')),
    path('api/integrations/', include('integrations.urls')),
    path('api/inscricoes/', include('inscricoes.urls')),
    
    # Documentação Swagger/OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
