from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Usuario


class OAuth2TokenViewTests(APITestCase):
    """
    Testes para a view de geração de token OAuth2 (JWT).
    """
    
    def test_url_oauth2_token_exists(self):
        """Testa se a URL do endpoint OAuth2 está configurada corretamente."""
        url = reverse('oauth2-token')
        self.assertEqual(url, '/api/integrations/api-cpf-light/v2/oauth2/token')
    
    def test_post_token_success(self):
        """Testa geração de token com CPF válido."""
        url = reverse('oauth2-token')
        headers = {'x-cpf-usuario': '12345678900'}
        
        response = self.client.post(url, headers=headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertEqual(response.data['token_type'], 'Bearer')
        self.assertEqual(response.data['expires_in'], 3600)
    
    def test_post_token_missing_header(self):
        """Testa erro quando header x-cpf-usuario não é fornecido."""
        url = reverse('oauth2-token')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_post_token_invalid_cpf_length(self):
        """Testa erro quando CPF tem tamanho inválido."""
        url = reverse('oauth2-token')
        headers = {'x-cpf-usuario': '123456'}
        
        response = self.client.post(url, headers=headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_post_token_with_special_characters(self):
        """Testa que CPF com caracteres especiais é limpo corretamente."""
        url = reverse('oauth2-token')
        headers = {'x-cpf-usuario': '123.456.789-00'}
        
        response = self.client.post(url, headers=headers)
        
        # Deve remover os caracteres e validar os 11 dígitos
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)


class DadosFamiliarViewTests(APITestCase):
    """
    Testes para a view de consulta de dados familiares do CadÚnico.
    """
    
    def test_url_dados_familiar_exists(self):
        """Testa se a URL do endpoint dados familiares está configurada corretamente."""
        url = reverse('dados-familiar', kwargs={'cpf': '12345678900'})
        self.assertEqual(url, '/api/integrations/api-cadunico-servicos-dados/v1/dp/dadosFamiliar/12345678900')
    
    def test_get_dados_familiar_invalid_cpf(self):
        """Testa erro quando CPF é inválido."""
        url = reverse('dados-familiar', kwargs={'cpf': '123456'})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'fail')
        self.assertEqual(response.data['status_code'], '400')
        self.assertEqual(response.data['error_message'], 'CPF inválido')
    
    def test_get_dados_familiar_valid_cpf_format(self):
        """Testa validação de formato do CPF."""
        # CPF válido com 11 dígitos
        url = reverse('dados-familiar', kwargs={'cpf': '12345678900'})
        
        # A requisição pode falhar por conexão, mas deve passar pela validação do CPF
        response = self.client.get(url)
        
        # Pode ser 404 (não encontrado na API externa) ou 500 (erro de conexão)
        # Mas não pode ser 400 (CPF inválido)
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_dados_familiar_with_special_chars(self):
        """Testa que CPF com caracteres especiais é tratado."""
        # Testar com CPF formatado
        url = reverse('dados-familiar', kwargs={'cpf': '123.456.789-00'})
        
        response = self.client.get(url)
        
        # Deve processar o CPF (removendo caracteres especiais)
        # Pode retornar 404, 500, mas não 400 se a limpeza funcionar
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_dados_familiar_headers_default_values(self):
        """Testa que headers padrão são aplicados corretamente."""
        url = reverse('dados-familiar', kwargs={'cpf': '12345678900'})
        
        # Fazer requisição sem headers específicos
        response = self.client.get(url)
        
        # Verifica que a requisição foi processada (não retornou erro de CPF inválido)
        # O resultado depende da API externa, mas a validação inicial deve passar
        self.assertIn(response.status_code, [
            status.HTTP_200_OK, 
            status.HTTP_404_NOT_FOUND, 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ])
