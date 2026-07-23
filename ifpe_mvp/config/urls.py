"""
URLs principais do projeto IFPE MVP
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),
    
    # API REST com documentação Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Apps do projeto
    path('', include('apps.core.urls')),
    path('students/', include('apps.students.urls', namespace='students')),
    path('family/', include('apps.family.urls')),
    path('enrollments/', include('apps.enrollments.urls')),
    path('api/v1/', include('apps.api.urls')),
    # Integrações com APIs externas (QAcadêmico, ConectaGov)
    path('api/', include('integrations.urls')),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
