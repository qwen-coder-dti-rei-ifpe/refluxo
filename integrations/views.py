"""
Views do app integrations - Views para integrações com APIs externas.

Este módulo contém as views da API REST para integração com
QAcadêmico e ConectaGov, incluindo consulta de elegibilidade.
"""
import requests
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings


class OAuthTokenView(APIView):
    """
    View para obtenção de token OAuth para API CPF Light.
    
    Endpoint: POST /api-cpf-light/v2/oauth2/token
    
    Requer header x-cpf-usuario com o CPF do usuário.
    Retorna um token JWT de acesso.
    """
    
    def post(self, request):
        """Gera e retorna um token de acesso OAuth."""
        # Obter CPF do header
        cpf = request.headers.get('x-cpf-usuario')
        
        if not cpf:
            return Response(
                {'error': 'Header x-cpf-usuario é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar formato do CPF (opcional - pode ser removido se não necessário)
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        if len(cpf_limpo) != 11:
            return Response(
                {'error': 'CPF inválido. Deve conter 11 dígitos.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Importar serviço OAuth
            from integrations.oauth_service import gerar_token_acesso
            
            # Gerar token de acesso
            access_token = gerar_token_acesso(cpf_limpo)
            
            return Response({
                'access_token': access_token
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Erro ao gerar token: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


from integrations.oauth_service import gerar_token_acesso


class DadosFamiliarView(APIView):
    """
    View para consulta de dados familiares do CadÚnico.
    
    Endpoint: GET /api-cadunico-servicos-dados/v1/dp/dadosFamiliar/{cpf}
    
    Integra com API externa CadÚnico para obter dados familiares do cidadão.
    Requer token OAuth obtido via endpoint /api-cpf-light/v2/oauth2/token.
    """
    
    def get(self, request, cpf=None):
        """Consulta dados familiares do CPF informado."""
        from integrations.cadunico_service import buscar_dados_familiar, validar_cpf
        
        # Validar CPF
        if not cpf:
            return Response(
                {'error': 'CPF é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar formato do CPF
        if not validar_cpf(cpf):
            return Response(
                {'status': 'fail', 'status_code': '400', 'error_message': 'CPF inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obter token de autorização do header ou gerar novo
        auth_header = request.headers.get('Authorization')
        access_token = None
        
        if auth_header and auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
        else:
            # Gerar novo token usando o serviço OAuth
            try:
                access_token = gerar_token_acesso(cpf)
            except Exception as e:
                return Response(
                    {'status': 'fail', 'status_code': '500', 'error_message': 'Erro ao gerar token de acesso'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Consultar API CadÚnico
        dados_api, erro = buscar_dados_familiar(cpf, access_token)
        
        if dados_api:
            return Response(dados_api, status=status.HTTP_200_OK)
        else:
            # Mapear erros para respostas padronizadas
            if erro == "CPF inválido":
                return Response(
                    {'status': 'fail', 'status_code': '400', 'error_message': erro},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif erro == "CPF não encontrado":
                return Response(
                    {'status': 'fail', 'status_code': '404', 'error_message': erro},
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                return Response(
                    {'status': 'fail', 'status_code': '500', 'error_message': 'Erro Interno no Sistema. Tente mais tarde'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


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
