"""
Testes unitários para o aplicativo Enrollments.

Estes testes verificam se as inscrições são criadas corretamente
na tabela Inscricoes quando um estudante submete uma enrollment.
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from ifpe_mvp.apps.students.models import Student
from ifpe_mvp.apps.enrollments.models import Enrollment, EnrollmentPeriod, Displacement
from inscricoes.models import Edital, Inscricao, Estudante
from core.models import Usuario as User


class EnrollmentSubmissionTestCase(TestCase):
    """
    Testes para verificar a criação de inscrições na tabela Inscricoes
    quando um estudante submete uma enrollment.
    """
    
    def setUp(self):
        """Configura os dados necessários para os testes."""
        # Criar usuário de teste
        self.user = User.objects.create_user(
            username='12345678900',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar estudante com CPF 12345678900 e matrícula 20222F32RC0286
        self.student = Student.objects.create(
            cpf='12345678900',
            nome_completo='João da Silva',
            matricula='20222F32RC0286',
            email_institucional='joao.silva@ifpe.edu.br',
            curso='Informática',
            campus='Recife',
            data_nascimento='2000-01-15',
            raca='Parda',
            sexo='M',
            user=self.user,
        )
        
        # Criar período de inscrição (Edital) ativo e dentro do período
        agora = timezone.now()
        self.period = EnrollmentPeriod.objects.create(
            titulo='Edital Teste 2025',
            descricao='Edital para teste',
            data_inicio=agora - timedelta(days=1),
            data_fim=agora + timedelta(days=30),
            status='ABERTO',
            ativo=True,
        )
        
        # Criar deslocamento
        self.displacement = Displacement.objects.create(
            valor_mensal_transporte=100.00,
            trajeto_percorrido='Casa -> IFPE Recife',
            tipo_transporte='ONIBUS',
        )
    
    def test_enrollment_creates_inscricao_on_submit(self):
        """
        Testa se ao submeter uma enrollment, uma instância em Inscricoes é criada.
        
        Este teste verifica:
        1. Se o estudante é criado na tabela core_estudante
        2. Se a inscrição é criada na tabela inscricoes_inscricao
        3. Se o status e classificação estão corretos
        """
        # Criar enrollment
        enrollment = Enrollment.objects.create(
            student=self.student,
            enrollment_period=self.period,
            status='RASCUNHO',
            displacement=self.displacement,
            renda_bruta_familiar=1500.00,
            renda_per_capita=375.00,
            faixa_renda_per_capita='ATE_05_SALARIOS',
            relato_vida='Teste de relato de vida',
            eh_chefe_familia=False,
            beneficiario_social=False,
            declaracao_veracidade=True,
        )
        
        # Verificar que não existe inscrição antes da submissão
        inscricoes_antes = Inscricao.objects.filter(estudante__cpf='12345678900').count()
        self.assertEqual(inscricoes_antes, 0, "Não deveria existir inscrição antes da submissão")
        
        # Submeter a enrollment
        enrollment.submeter()
        
        # Atualizar enrollment do banco
        enrollment.refresh_from_db()
        
        # Verificar se a enrollment foi atualizada corretamente
        self.assertEqual(enrollment.status, 'SUBMETIDA', "Status da enrollment deveria ser SUBMETIDA")
        self.assertEqual(enrollment.classificacao, 'ANALISE', "Classificação deveria ser ANALISE")
        
        # Verificar se o estudante foi criado na tabela core_estudante
        estudante_obj = Estudante.objects.get(cpf='12345678900')
        self.assertIsNotNone(estudante_obj, "Estudante deveria ser criado na tabela core_estudante")
        self.assertEqual(estudante_obj.nome_completo, 'João da Silva')
        
        # Verificar se a instância em Inscricoes foi criada
        inscricao = Inscricao.objects.filter(estudante=estudante_obj).first()
        self.assertIsNotNone(inscricao, "Inscrição deveria ser criada na tabela inscricoes_inscricao")
        
        # Verificar dados da inscrição
        self.assertEqual(inscricao.status, 'SUBMETIDA', "Status da inscrição deveria ser SUBMETIDA")
        self.assertEqual(inscricao.classificacao, 'ANALISE', "Classificação deveria ser ANALISE")
        self.assertIsNotNone(inscricao.submetida_em, "Data de submissão deveria estar preenchida")
        
        # Verificar informações do estudante na inscrição
        self.assertIn('nome', inscricao.informacoes_estudante)
        self.assertEqual(inscricao.informacoes_estudante['cpf'], '12345678900')
        self.assertEqual(inscricao.informacoes_estudante['matricula'], '20222F32RC0286')
    
    def test_enrollment_updates_existing_inscricao(self):
        """
        Testa se ao submeter uma enrollment novamente, a inscrição existente é atualizada.
        """
        # Criar e submeter enrollment pela primeira vez
        enrollment = Enrollment.objects.create(
            student=self.student,
            enrollment_period=self.period,
            status='RASCUNHO',
            displacement=self.displacement,
            renda_bruta_familiar=1500.00,
            renda_per_capita=375.00,
            faixa_renda_per_capita='ATE_05_SALARIOS',
            relato_vida='Teste de relato de vida',
            eh_chefe_familia=False,
            beneficiario_social=False,
            declaracao_veracidade=True,
        )
        
        enrollment.submeter()
        
        # Obter a inscrição criada
        estudante_obj = Estudante.objects.get(cpf='12345678900')
        inscricao = Inscricao.objects.filter(estudante=estudante_obj).first()
        
        # Simular nova submissão (atualização)
        enrollment.status = 'RASCUNHO'
        enrollment.renda_bruta_familiar = 2000.00
        enrollment.save()
        enrollment.submeter()
        
        # Verificar que ainda existe apenas uma inscrição
        inscricoes_count = Inscricao.objects.filter(estudante=estudante_obj).count()
        self.assertEqual(inscricoes_count, 1, "Deveria existir apenas uma inscrição")
        
        # Verificar que a inscrição foi atualizada
        inscricao.refresh_from_db()
        self.assertEqual(inscricao.status, 'SUBMETIDA')


class SocialWorkerClassificationTestCase(TestCase):
    """
    Testes para verificar se o assistente social pode classificar as inscrições.
    """
    
    def setUp(self):
        """Configura os dados necessários para os testes."""
        # Criar usuário de teste
        self.user = User.objects.create_user(
            username='12345678900',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar estudante
        self.student = Student.objects.create(
            cpf='12345678900',
            nome_completo='João da Silva',
            matricula='20222F32RC0286',
            email_institucional='joao.silva@ifpe.edu.br',
            curso='Informática',
            campus='Recife',
            data_nascimento='2000-01-15',
            raca='Parda',
            sexo='M',
            user=self.user,
        )
        
        # Criar período de inscrição
        agora = timezone.now()
        self.period = EnrollmentPeriod.objects.create(
            titulo='Edital Teste 2025',
            descricao='Edital para teste',
            data_inicio=agora - timedelta(days=1),
            data_fim=agora + timedelta(days=30),
            status='ABERTO',
            ativo=True,
        )
        
        # Criar enrollment e submeter
        self.displacement = Displacement.objects.create(
            valor_mensal_transporte=100.00,
            trajeto_percorrido='Casa -> IFPE Recife',
            tipo_transporte='ONIBUS',
        )
        
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            enrollment_period=self.period,
            status='RASCUNHO',
            displacement=self.displacement,
            renda_bruta_familiar=1500.00,
            renda_per_capita=375.00,
            faixa_renda_per_capita='ATE_05_SALARIOS',
            relato_vida='Teste de relato de vida',
            eh_chefe_familia=False,
            beneficiario_social=False,
            declaracao_veracidade=True,
        )
        
        self.enrollment.submeter()
    
    def test_social_worker_can_classify_enrollment(self):
        """
        Testa se o assistente social pode classificar uma inscrição.
        """
        # Obter a inscrição criada
        estudante_obj = Estudante.objects.get(cpf='12345678900')
        inscricao = Inscricao.objects.filter(estudante=estudante_obj).first()
        
        self.assertIsNotNone(inscricao, "Inscrição deveria existir")
        self.assertEqual(inscricao.classificacao, 'ANALISE', "Classificação inicial deveria ser ANALISE")
        
        # Classificar a inscrição (simulando ação do assistente social)
        self.enrollment.classificar(
            classificacao='ELEGIVEL',
            assistente_social='Maria Santos',
            comentario='Estudante atende todos os critérios de elegibilidade'
        )
        
        # Verificar se a classificação foi atualizada
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.classificacao, 'ELEGIVEL')
        self.assertEqual(self.enrollment.assistente_social_responsavel, 'Maria Santos')
        self.assertIsNotNone(self.enrollment.data_classificacao)
        self.assertIn('atende todos os critérios', self.enrollment.comentario_assistente_social)
