"""
Views do app integrations - Views para integrações com APIs externas.

Este módulo contém as views da API REST para integração com
QAcadêmico, ConectaGov, incluindo consulta de elegibilidade e OAuth2.
"""
import requests
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.conf import settings
from datetime import timedelta
import re


def validar_cpf(cpf):
    """
    Valida o formato do CPF.
    Remove caracteres especiais e verifica se tem 11 dígitos.
    """
    if not cpf:
        return None
    
    # Remove caracteres não numéricos
    cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
    
    # Verifica se tem 11 dígitos
    if len(cpf_limpo) != 11:
        return None
    
    return cpf_limpo


class QAcademicoViewSet(viewsets.ViewSet):
    """
    ViewSet para integração com API QAcadêmico (mock).
    
    Fornece endpoints para consultar dados acadêmicos do estudante
    usando matrícula como identificador.
    """
    
    @action(detail=False, methods=['get'], url_path='student/(?P<matricula>[^/.]+)')
    def student(self, request, matricula=None):
        """Consulta dados completos do estudante pela matrícula na API Mock do QAcadêmico."""
        if not matricula:
            return Response(
                {'success': False, 'error': 'Matrícula é obrigatória'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Importar serviço de integração com QAcadêmico
        try:
            from integrations.qacademico_service import buscar_estudante_qacademico
            
            dados_api, erro = buscar_estudante_qacademico(matricula)
            
            if dados_api:
                # Formatar data de nascimento para DD/MM/YYYY
                data_nascimento_fmt = ''
                if dados_api.get('data_nascimento'):
                    try:
                        from datetime import datetime
                        date_obj = datetime.strptime(dados_api.get('data_nascimento'), '%Y-%m-%d')
                        data_nascimento_fmt = date_obj.strftime('%d/%m/%Y')
                    except (ValueError, TypeError):
                        data_nascimento_fmt = dados_api.get('data_nascimento', '')
                
                # Mapear dados para formato esperado pelo frontend
                dados_formatados = {
                    'nome_completo': dados_api.get('nome_completo', ''),
                    'cpf': dados_api.get('cpf', ''),
                    'identidade': dados_api.get('identidade', ''),
                    'data_nascimento': dados_api.get('data_nascimento', ''),
                    'data_nascimento_fmt': data_nascimento_fmt,
                    'idade': dados_api.get('idade', 0),
                    'raca': dados_api.get('raca', ''),
                    'sexo': dados_api.get('sexo', ''),
                    'genero': dados_api.get('genero', dados_api.get('sexo', '')),
                    'matricula': dados_api.get('matricula', ''),
                    'campus': dados_api.get('campus', ''),
                    'curso': dados_api.get('curso', ''),
                    'turno': dados_api.get('turno', ''),
                    'periodo': dados_api.get('periodo', ''),
                    'eh_cotista': dados_api.get('eh_cotista', False),
                    'email': dados_api.get('email', ''),
                    'email_institucional': dados_api.get('email_institucional', dados_api.get('email', '')),
                    'email_pessoal': dados_api.get('email_pessoal', dados_api.get('email', '')),
                    'nome_mae': dados_api.get('nome_mae', ''),
                    'nome_pai': dados_api.get('nome_pai', ''),
                }
                
                return Response({
                    'success': True,
                    'dados': dados_formatados,
                    'mensagem': 'Dados encontrados com sucesso'
                })
            else:
                return Response({
                    'success': False,
                    'error': erro or 'Estudante não encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Erro ao consultar API QAcadêmico: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def consultar(self, request):
        """Consulta dados do estudante pela matrícula."""
        matricula = request.query_params.get('matricula')
        
        if not matricula:
            return Response(
                {'error': 'Matrícula é obrigatória'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mock de dados - em produção faria chamada HTTP para API QAcadêmico
        dados_mock = {
            'matricula': matricula,
            'nome_estudante': f'Estudante Exemplo {matricula}',
            'curso': 'Técnico em Informática',
            'campus': 'Recife',
            'periodo': '3º',
            'turno': 'MATUTINO',
            'status_matricula': 'ATIVO'
        }
        
        return Response(dados_mock)
    
    @action(detail=False, methods=['get'])
    def validar_matricula(self, request):
        """Valida se a matrícula existe e está ativa."""
        matricula = request.query_params.get('matricula')
        
        if not matricula:
            return Response(
                {'error': 'Matrícula é obrigatória'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mock de validação
        valido = True  # Em produção consultaria a API real
        
        return Response({
            'matricula': matricula,
            'valida': valido,
            'mensagem': 'Matrícula válida' if valido else 'Matrícula inválida ou inativa'
        })


class ConectaGovViewSet(viewsets.ViewSet):
    """
    ViewSet para integração com API ConectaGov (mock).
    
    Fornece endpoints para consultar dados do cidadão no
    CadÚnico/CBC usando CPF como identificador.
    """
    
    @action(detail=False, methods=['get'])
    def consultar(self, request):
        """Consulta dados do cidadão pelo CPF."""
        cpf = request.query_params.get('cpf')
        
        if not cpf:
            return Response(
                {'error': 'CPF é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mock de dados - em produção faria chamada HTTP para API ConectaGov
        dados_mock = {
            'cpf': cpf,
            'nome_cidadao': f'Cidadão Exemplo {cpf}',
            'nis': '12345678901',
            'possui_cadastro_unico': True,
            'renda_per_capita': 450.00,
            'familiares': [
                {
                    'nome': 'Familiar 1',
                    'cpf': '12345678900',
                    'parentesco': 'MÃE',
                    'renda': 1200.00
                },
                {
                    'nome': 'Familiar 2',
                    'cpf': '09876543210',
                    'parentesco': 'IRMÃO',
                    'renda': 0.00
                }
            ],
            'beneficios_sociais': [
                {'programa': 'Bolsa Família', 'valor': 600.00}
            ]
        }
        
        return Response(dados_mock)
    
    @action(detail=False, methods=['get'])
    def verificar_beneficios(self, request):
        """Verifica benefícios sociais do cidadão."""
        cpf = request.query_params.get('cpf')
        
        if not cpf:
            return Response(
                {'error': 'CPF é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mock de verificação
        beneficios = [
            {'programa': 'Bolsa Família', 'ativo': True, 'valor': 600.00},
            {'programa': 'BPC', 'ativo': False, 'valor': 0.00}
        ]
        
        return Response({
            'cpf': cpf,
            'beneficios': beneficios
        })


class ConsultaElegibilidadeView(APIView):
    """
    View para consulta completa de elegibilidade do estudante.
    
    Integra dados do QAcadêmico e ConectaGov para determinar
    se o estudante é elegível ao programa de apoio estudantil.
    """
    
    def get(self, request):
        """Consulta elegibilidade baseada em matrícula ou CPF."""
        matricula = request.query_params.get('matricula')
        cpf = request.query_params.get('cpf')
        
        if not matricula and not cpf:
            return Response(
                {'error': 'Matrícula ou CPF são obrigatórios'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simula integração com APIs
        dados_qacademico = {
            'matricula_valida': True,
            'curso': 'Técnico em Informática',
            'periodo': '3º',
            'status': 'ATIVO'
        }
        
        dados_conecta_gov = {
            'cadastro_unico': True,
            'renda_per_capita': 450.00,
            'possui_beneficio': True,
            'familiares_count': 3
        }
        
        # Regras de elegibilidade
        elegivel = (
            dados_qacademico['matricula_valida'] and
            dados_qacademico['status'] == 'ATIVO' and
            dados_conecta_gov['renda_per_capita'] <= 800.00
        )
        
        return Response({
            'elegivel': elegivel,
            'dados_academicos': dados_qacademico,
            'dados_socioeconomicos': dados_conecta_gov,
            'motivos': self._gerar_motivos(elegivel, dados_qacademico, dados_conecta_gov)
        })
    
    def _gerar_motivos(self, elegivel, qacademico, conecta_gov):
        """Gera lista de motivos para elegibilidade ou inelegibilidade."""
        motivos = []
        
        if elegivel:
            motivos.append('Estudante matriculado e ativo')
            motivos.append('Renda per capita dentro do limite')
            if conecta_gov.get('possui_beneficio'):
                motivos.append('Possui benefício social ativo')
        else:
            if not qacademico.get('matricula_valida'):
                motivos.append('Matrícula inválida')
            if qacademico.get('status') != 'ATIVO':
                motivos.append('Matrícula não está ativa')
            if conecta_gov.get('renda_per_capita', 0) > 800.00:
                motivos.append('Renda per capita acima do limite permitido')
        
        return motivos


class OAuth2TokenView(APIView):
    """
    View para geração de token OAuth2 (JWT) para integração com API CPF Light.
    
    Endpoint: POST /api-cpf-light/v2/oauth2/token
    Header necessário: x-cpf-usuario (CPF do usuário)
    
    Retorna um JWT token de acesso para autenticação nas requisições subsequentes.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, format=None):
        """Gera token JWT de acesso baseado no CPF do usuário."""
        # Obter CPF do header
        cpf_usuario = request.headers.get('x-cpf-usuario')
        
        if not cpf_usuario:
            return Response(
                {'error': 'Header x-cpf-usuario é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar formato do CPF (apenas números, 11 dígitos)
        cpf_limpo = validar_cpf(cpf_usuario)
        
        if not cpf_limpo:
            return Response(
                {'error': 'CPF deve conter 11 dígitos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Importar SimpleJWT para gerar token
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            
            # Tentar obter ou criar usuário temporário para o CPF
            user, created = User.objects.get_or_create(
                username=cpf_limpo,
                defaults={
                    'cpf': cpf_limpo,
                    'email': f'{cpf_limpo}@cpf-light.local',
                }
            )
            
            # Gerar tokens para o usuário
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access_token': str(refresh.access_token),
                'token_type': 'Bearer',
                'expires_in': 3600,  # 1 hora em segundos
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Erro ao gerar token: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DadosFamiliarView(APIView):
    """
    View para consulta de dados familiares via API CadÚnico.
    
    Endpoint: GET /api-cadunico-servicos-dados/v1/dp/dadosFamiliar/{cpf}
    
    Consulta os dados do cidadão e sua família baseado no CPF.
    Requer autenticação via token JWT e headers específicos de identificação.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, cpf, format=None):
        """
        Consulta dados familiares do CPF na API externa do CadÚnico.
        
        Headers necessários:
        - Accept-Language: application/json
        - Content-Type: application/json
        - cpf: CPF do usuário
        - X-Consumer-Id: Identificação do consumidor (ex: AGU, CPF, CNPJ)
        - X-Consumer-Id-Type: Tipo da chave (Sigla, CPF, CNPJ)
        - X-Authorization-Id: ID da autorização (processo, contrato, etc)
        - X-Authorization-Id-Type: Tipo da autorização (Processo, Contrato, Consentimento)
        - Authorization: Bearer <token>
        """
        # Validar CPF
        cpf_limpo = validar_cpf(cpf)
        
        if not cpf_limpo:
            return Response({
                'status': 'fail',
                'status_code': '400',
                'error_message': 'CPF inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obter headers da requisição
        accept_language = request.headers.get('Accept-Language', 'application/json')
        content_type = request.headers.get('Content-Type', 'application/json')
        header_cpf = request.headers.get('cpf', cpf_limpo)
        consumer_id = request.headers.get('X-Consumer-Id', 'IFPE')
        consumer_id_type = request.headers.get('X-Consumer-Id-Type', 'Sigla')
        authorization_id = request.headers.get('X-Authorization-Id', '0002452-51.2016.2.00.0001')
        authorization_id_type = request.headers.get('X-Authorization-Id-Type', 'Processo')
        auth_header = request.headers.get('Authorization', '')
        
        # URL base da API externa (mock)
        # Em produção, usar settings.EXTERNAL_API_BASE_URL ou variável de ambiente
        base_url = getattr(settings, 'CADUNICO_API_BASE_URL', 'https://ee18227e-74c8-4cf4-97c0-daa3f5908982.mock.pstmn.io')
        endpoint_url = f"{base_url}/api-cadunico-servicos-dados/v1/dp/dadosFamiliar/{cpf_limpo}"
        
        # Preparar headers para requisição externa
        headers = {
            'Accept-Language': accept_language,
            'Content-Type': content_type,
            'cpf': header_cpf,
            'X-Consumer-Id': consumer_id,
            'X-Consumer-Id-Type': consumer_id_type,
            'X-Authorization-Id': authorization_id,
            'X-Authorization-Id-Type': authorization_id_type,
        }
        
        # Adicionar Authorization se presente
        if auth_header:
            headers['Authorization'] = auth_header
        
        try:
            # Fazer requisição para API externa
            response = requests.get(endpoint_url, headers=headers, timeout=30)
            
            # Tratar resposta da API externa
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Retornar dados no formato esperado
                    return Response(data, status=status.HTTP_200_OK)
                except ValueError:
                    # Resposta não é JSON válido
                    return Response({
                        'status': 'fail',
                        'status_code': '500',
                        'error_message': 'Erro Interno no Sistema. Tente mais tarde'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            elif response.status_code == 404:
                return Response({
                    'status': 'fail',
                    'status_code': '404',
                    'error_message': 'CPF não encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
            
            elif response.status_code == 400:
                return Response({
                    'status': 'fail',
                    'status_code': '400',
                    'error_message': 'CPF inválido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                # Outros erros da API externa
                return Response({
                    'status': 'fail',
                    'status_code': '500',
                    'error_message': 'Erro Interno no Sistema. Tente mais tarde'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except requests.exceptions.RequestException as e:
            # Erro de conexão ou timeout
            return Response({
                'status': 'fail',
                'status_code': '500',
                'error_message': 'Erro Interno no Sistema. Tente mais tarde'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Erro inesperado
            return Response({
                'status': 'fail',
                'status_code': '500',
                'error_message': 'Erro Interno no Sistema. Tente mais tarde'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
