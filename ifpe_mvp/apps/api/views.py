"""
Views do aplicativo API - ViewSets e endpoints REST
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from students.models import Student
from family.models import Address, FamilyMember
from enrollments.models import EnrollmentPeriod, Enrollment, Displacement

from .serializers import (
    StudentSerializer,
    AddressSerializer,
    FamilyMemberSerializer,
    DisplacementSerializer,
    EnrollmentPeriodSerializer,
    EnrollmentSerializer,
    EnrollmentCreateSerializer,
)


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de estudantes.
    Permite busca por matrícula, CPF e nome.
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['matricula', 'cpf', 'campus', 'curso']
    search_fields = ['nome_completo', 'matricula', 'cpf']
    ordering_fields = ['nome_completo', 'matricula', 'criado_em']
    ordering = ['nome_completo']


class EnrollmentPeriodViewSet(viewsets.ModelViewSet):
    """
    ViewSet para períodos de inscrição (editais).
    """
    queryset = EnrollmentPeriod.objects.all()
    serializer_class = EnrollmentPeriodSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ativo', 'status']


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para inscrições dos estudantes.
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['student', 'enrollment_period', 'status']
    ordering_fields = ['criado_em', 'data_conclusao']
    ordering = ['-criado_em']
    
    def get_serializer_class(self):
        """Retorna serializer diferente para criação."""
        if self.action == 'create':
            return EnrollmentCreateSerializer
        return EnrollmentSerializer
    
    def perform_create(self, serializer):
        """Cria inscrição com status inicial."""
        serializer.save(status='RASCUNHO')


@api_view(['GET'])
@permission_classes([AllowAny])
def connecta_gov_mock(request):
    """
    Mock da API ConectaGov para simular integração com CBC/CadÚnico.
    Retorna dados fictícios para desenvolvimento e testes.
    """
    # Em produção, isso seria uma chamada real à API do ConectaGov
    mock_data = {
        'cpf': '12345678900',
        'nome': 'João da Silva',
        'cadunico': {
            'nis': '12345678900',
            'familia': {
                'membros': [
                    {
                        'nome': 'Maria da Silva',
                        'cpf': '98765432100',
                        'parentesco': 'MAE',
                        'renda': 1200.00,
                    },
                    {
                        'nome': 'José da Silva',
                        'cpf': '45678912300',
                        'parentesco': 'PAI',
                        'renda': 1500.00,
                    }
                ],
                'renda_total': 2700.00,
                'per_capita': 900.00,
            },
            'beneficios': [
                {
                    'programa': 'Bolsa Família',
                    'valor': 600.00,
                    'titular': 'Maria da Silva',
                }
            ]
        },
        'elegibilidade': {
            'renda_per_capita_ate_1_salario': True,
            'beneficiario_programa_social': True,
        }
    }
    
    return Response(mock_data)


class QAcademicoMockView(APIView):
    """
    Mock da API QAcadêmico para simular integração com sistema acadêmico.
    Retorna dados fictícios do estudante.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        matricula = request.query_params.get('matricula', None)
        
        # Em produção, isso seria uma chamada real ao QAcadêmico
        mock_data = {
            'matricula': matricula or '20241001001',
            'nome': 'João da Silva',
            'curso': 'Técnico em Informática',
            'campus': 'Recife',
            'turno': 'MATUTINO',
            'periodo': 3,
            'situacao': 'ATIVO',
            'disciplinas': [
                {'codigo': 'INF001', 'nome': 'Programação I', 'carga_horaria': 80},
                {'codigo': 'INF002', 'nome': 'Banco de Dados', 'carga_horaria': 60},
            ],
            'historico': {
                'media_geral': 8.5,
                'frequencia': 95.0,
            }
        }
        
        return Response(mock_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_student_by_matricula(request):
    """
    Busca dados do estudante por matrícula.
    Primeiro verifica no banco de dados local, depois na API QAcadêmico.
    """
    from students.models import Student
    
    matricula = request.query_params.get('matricula', None)
    
    if not matricula:
        return Response({'error': 'Matrícula não fornecida'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Primeiro, busca no banco de dados local
    try:
        student = Student.objects.get(matricula=matricula)
        data = {
            'fonte': 'banco_dados',
            'matricula': student.matricula or '',
            'nome_completo': student.nome_completo or '',
            'cpf': student.cpf or '',
            'identidade': student.identidade or '',
            'data_nascimento': student.data_nascimento.strftime('%Y-%m-%d') if student.data_nascimento else '',
            'idade': student.idade or '',
            'raca': student.raca or '',
            'sexo': student.sexo or '',
            'genero': student.genero or student.sexo or '',
            'campus': student.campus or '',
            'curso': student.curso or '',
            'turno': student.turno or '',
            'periodo': str(student.periodo) if student.periodo else '',
            'eh_cotista': student.eh_cotista,
            'email_pessoal': student.email_pessoal or '',
            'origem_escolar': student.origem_escolar or '',
            'moradia_estudantil': student.moradia_estudantil,
            'tipo_conta': student.tipo_conta or '',
            'numero_agencia': student.numero_agencia or '',
            'numero_conta': student.numero_conta or '',
            'banco': student.banco or '',
            'banco_outro': student.banco_outro or '',
        }
        return Response(data)
    except Student.DoesNotExist:
        pass
    
    # Se não encontrou no banco, busca na API QAcadêmico (mock)
    mock_data = {
        'fonte': 'qacademico',
        'matricula': matricula,
        'nome_completo': 'João da Silva',
        'cpf': '',
        'identidade': '',
        'data_nascimento': '',
        'idade': '',
        'raca': '',
        'sexo': '',
        'genero': '',
        'campus': 'Recife',
        'curso': 'Técnico em Informática',
        'turno': 'MATUTINO',
        'periodo': '3',
        'eh_cotista': False,
        'email_pessoal': '',
        'origem_escolar': '',
        'moradia_estudantil': False,
        'tipo_conta': '',
        'numero_agencia': '',
        'numero_conta': '',
        'banco': '',
        'banco_outro': '',
    }
    
    return Response(mock_data)
