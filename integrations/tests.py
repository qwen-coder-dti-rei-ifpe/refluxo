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
