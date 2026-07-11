"""
URLs do aplicativo API - Endpoints REST
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet, 
    EnrollmentPeriodViewSet, 
    EnrollmentViewSet,
    ConnectaGovMockView,
    QAcademicoMockView,
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'enrollment-periods', EnrollmentPeriodViewSet, basename='enrollment-period')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    # Rotas do router DRF
    path('', include(router.urls)),
    
    # Mocks de integração
    path('connecta-gov/', ConnectaGovMockView.as_view(), name='connecta-gov-mock'),
    path('qacademico/', QAcademicoMockView.as_view(), name='qacademico-mock'),
]
