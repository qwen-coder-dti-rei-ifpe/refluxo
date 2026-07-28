"""
Serviço de integração com API CadÚnico - Dados Familiar.

Este módulo contém a lógica para consumo da API externa
de dados familiares do CadÚnico.
"""
import requests
from django.conf import settings


def buscar_dados_familiar(cpf: str, access_token: str) -> tuple[dict | None, str | None]:
    """
    Consulta os dados familiares do cidadão na API CadÚnico.
    
    Args:
        cpf: CPF do cidadão (11 dígitos)
        access_token: Token JWT de autorização
        
    Returns:
        tuple: (dados_api, erro) - dados_api é um dict com os dados retornados
               ou None em caso de erro, erro é uma string com mensagem de erro
               ou None se sucesso
    """
    # URL base da API
    base_url = getattr(
        settings, 
        'CADUNICO_API_BASE_URL', 
        'https://ee18227e-74c8-4cf4-97c0-daa3f5908982.mock.pstmn.io'
    )
    
    # Endpoint específico
    endpoint = f"/api-cadunico-servicos-dados/v1/dp/dadosFamiliar/{cpf}"
    url = f"{base_url}{endpoint}"
    
    # Headers obrigatórios
    headers = {
        'Accept-Language': 'application/json',
        'Content-Type': 'application/json',
        'cpf': cpf,
        'X-Consumer-Id': getattr(settings, 'X_CONSUMER_ID', 'IFPE'),
        'X-Consumer-Id-Type': getattr(settings, 'X_CONSUMER_ID_TYPE', 'CPF'),
        'X-Authorization-Id': getattr(
            settings, 
            'X_AUTHORIZATION_ID', 
            '0002452-51.2016.2.00.0001'
        ),
        'X-Authorization-Id-Type': getattr(
            settings, 
            'X_AUTHORIZATION_ID_TYPE', 
            'Processo'
        ),
        'Authorization': f'Bearer {access_token}'
    }
    
    # Adicionar headers opcionais se configurados
    x_subject_id = getattr(settings, 'X_SUBJECT_ID', None)
    x_subject_type = getattr(settings, 'X_SUBJECT_TYPE', None)
    
    if x_subject_id:
        headers['X-Subject-Id'] = x_subject_id
    if x_subject_type:
        headers['X-Subject-Type'] = x_subject_type
    
    try:
        # Fazer requisição GET
        response = requests.get(url, headers=headers, timeout=30)
        
        # Tratar resposta
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 400:
            return None, "CPF inválido"
        elif response.status_code == 404:
            return None, "CPF não encontrado"
        elif response.status_code == 401:
            return None, "Token de autorização inválido ou expirado"
        elif response.status_code == 403:
            return None, "Acesso não autorizado"
        else:
            return None, f"Erro na API externa: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return None, "Timeout ao conectar com API CadÚnico"
    except requests.exceptions.ConnectionError:
        return None, "Erro de conexão com API CadÚnico"
    except requests.exceptions.RequestException as e:
        return None, f"Erro ao requisitar API CadÚnico: {str(e)}"
    except Exception as e:
        return None, f"Erro inesperado: {str(e)}"


def validar_cpf(cpf: str) -> bool:
    """
    Valida o formato do CPF.
    
    Args:
        cpf: CPF a ser validado
        
    Returns:
        bool: True se CPF válido (11 dígitos), False caso contrário
    """
    # Remover caracteres não numéricos
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    
    # Verificar se tem 11 dígitos
    if len(cpf_limpo) != 11:
        return False
    
    # Verificar se todos os dígitos são iguais (CPF inválido)
    if len(set(cpf_limpo)) == 1:
        return False
    
    return True
