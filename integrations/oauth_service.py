"""
Serviço de integração OAuth para API CPF Light.

Este módulo contém a lógica para obtenção de tokens OAuth
da API externa de consulta de CPF.
"""
import jwt
import datetime
from django.conf import settings


def gerar_token_acesso(cpf: str) -> str:
    """
    Gera um token JWT de acesso para o CPF informado.
    
    Args:
        cpf: CPF do usuário para quem o token será gerado
        
    Returns:
        string: Token JWT codificado
    """
    # Configurações do token
    secret_key = getattr(settings, 'OAUTH_SECRET_KEY', settings.SECRET_KEY)
    token_expiration_hours = getattr(settings, 'OAUTH_TOKEN_EXPIRATION_HOURS', 24)
    
    # Payload do token
    payload = {
        'cpf': cpf,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=token_expiration_hours),
        'iat': datetime.datetime.utcnow(),
        'type': 'access_token'
    }
    
    # Gerar token JWT
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    return token


def gerar_token_oauth(cpf: str) -> tuple[str | None, str | None]:
    """
    Gera um token OAuth para o CPF informado.
    Wrapper para gerar_token_acesso com tratamento de erros.
    
    Args:
        cpf: CPF do usuário para quem o token será gerado
        
    Returns:
        tuple: (token, erro) - token é uma string se sucesso, None se erro
               erro é uma string com mensagem de erro ou None se sucesso
    """
    try:
        token = gerar_token_acesso(cpf)
        return token, None
    except Exception as e:
        return None, f"Erro ao gerar token: {str(e)}"


def validar_token(token: str) -> dict:
    """
    Valida um token JWT e retorna o payload decodificado.
    
    Args:
        token: Token JWT a ser validado
        
    Returns:
        dict: Payload do token se válido
        
    Raises:
        jwt.ExpiredSignatureError: Se o token expirou
        jwt.InvalidTokenError: Se o token é inválido
    """
    secret_key = getattr(settings, 'OAUTH_SECRET_KEY', settings.SECRET_KEY)
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError('Token expirado')
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(f'Token inválido: {str(e)}')
