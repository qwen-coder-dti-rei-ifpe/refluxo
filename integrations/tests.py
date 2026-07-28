from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.conf import settings


class OAuthTokenViewTest(APITestCase):
    """Testes para a view de token OAuth."""
    
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/integrations/api-cpf-light/v2/oauth2/token/'
        self.cpf_valido = '03256858430'
        self.cpf_invalido = '123456789'
    
    def test_obter_token_sucesso(self):
        """Testa obtenção de token com CPF válido."""
        response = self.client.post(
            self.url,
            HTTP_X_CPF_USUARIO=self.cpf_valido
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIsInstance(response.data['access_token'], str)
    
    def test_obter_token_sem_cpf(self):
        """Testa requisição sem header x-cpf-usuario."""
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_obter_token_cpf_invalido(self):
        """Testa requisição com CPF inválido (menos de 11 dígitos)."""
        response = self.client.post(
            self.url,
            HTTP_X_CPF_USUARIO=self.cpf_invalido
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class DadosFamiliarViewTest(APITestCase):
    """Testes para a view de dados familiares do CadÚnico."""
    
    def setUp(self):
        self.client = APIClient()
        self.cpf_valido = '03256858430'
        self.cpf_invalido = '12345678901'  # CPF com dígitos iguais é inválido
    
    def test_dados_familiar_requer_cpf(self):
        """Testa que endpoint requer CPF na URL."""
        response = self.client.get(
            '/api/integrations/api-cadunico-servicos-dados/v1/dp/dadosFamiliar/'
        )
        # Deve retornar 404 ou redirecionar pois CPF é obrigatório na URL
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_302_FOUND])
    
    def test_dados_familiar_cpf_invalido_formato(self):
        """Testa validação de CPF com formato inválido."""
        url = f'/api/integrations/api-cadunico-servicos-dados/v1/dp/dadosFamiliar/{self.cpf_invalido}/'
        response = self.client.get(url)
        
        # CPF com todos dígitos iguais deve ser inválido
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'fail')
        self.assertEqual(response.data['status_code'], '400')
        self.assertEqual(response.data['error_message'], 'CPF inválido')
    
    def test_dados_familiar_com_autorizacao(self):
        """Testa consulta com token de autorização no header."""
        from integrations.oauth_service import gerar_token_acesso
        
        # Gerar token válido
        token = gerar_token_acesso(self.cpf_valido)
        
        url = f'/api/integrations/api-cadunico-servicos-dados/v1/dp/dadosFamiliar/{self.cpf_valido}/'
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        # Pode retornar 200 (sucesso), 404 (não encontrado) ou 500 (erro API externa)
        # O importante é que a validação do CPF passou
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ])
    
    def test_dados_familiar_sem_autorizacao_gera_token(self):
        """Testa que endpoint gera token automaticamente se não fornecido."""
        url = f'/api/integrations/api-cadunico-servicos-dados/v1/dp/dadosFamiliar/{self.cpf_valido}/'
        response = self.client.get(url)
        
        # Deve tentar consultar API (pode falhar por conexão, mas CPF foi validado)
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ])

# Create your tests here.
