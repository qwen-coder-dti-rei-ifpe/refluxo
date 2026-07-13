"""
Comando para popular o banco com dados mock para demonstração.
Cria:
- Usuário pedagogo
- Editais (períodos do programa)
- Estudantes mock
- Inscrições (submissões) dos estudantes
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Usuario, Estudante, Endereco
from inscricoes.models import Edital, Inscricao


class Command(BaseCommand):
    help = 'Popula o banco com dados mock para demonstração'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando usuário pedagogo...')
        
        # Criar usuário pedagogo se não existir
        pedagogo, created = Usuario.objects.get_or_create(
            username='pedagogo',
            defaults={
                'email': 'pedagogo@ifpe.edu.br',
                'is_pedagogo': True,
                'is_active': True,
            }
        )
        if created:
            pedagogo.set_password('pedagogo123')
            pedagogo.save()
            self.stdout.write(self.style.SUCCESS('Usuário pedagogo criado: username=pedagogo, senha=pedagogo123'))
        else:
            self.stdout.write('Usuário pedagogo já existe.')
        
        # Criar editais
        self.stdout.write('\nCriando editais...')
        agora = timezone.now()
        
        edital1, _ = Edital.objects.get_or_create(
            numero='01/2024',
            defaults={
                'titulo': 'Programa de Apoio e Manutenção Acadêmica - 2024.1',
                'descricao': 'Edital de seleção para concessão de bolsas de manutenção acadêmica para o primeiro semestre de 2024.',
                'periodo_inscricao_abertura': agora - timedelta(days=30),
                'periodo_inscricao_fechamento': agora + timedelta(days=15),
                'periodo_avaliacao_abertura': agora + timedelta(days=16),
                'periodo_avaliacao_fechamento': agora + timedelta(days=30),
                'status': 'ATIVO',
                'ativo': True,
            }
        )
        self.stdout.write(f'Edital criado: {edital1.numero}')
        
        edital2, _ = Edital.objects.get_or_create(
            numero='02/2024',
            defaults={
                'titulo': 'Programa de Apoio e Manutenção Acadêmica - 2024.2',
                'descricao': 'Edital de seleção para concessão de bolsas de manutenção acadêmica para o segundo semestre de 2024.',
                'periodo_inscricao_abertura': agora + timedelta(days=60),
                'periodo_inscricao_fechamento': agora + timedelta(days=90),
                'periodo_avaliacao_abertura': agora + timedelta(days=91),
                'periodo_avaliacao_fechamento': agora + timedelta(days=105),
                'status': 'ATIVO',
                'ativo': True,
            }
        )
        self.stdout.write(f'Edital criado: {edital2.numero}')
        
        # Criar estudantes mock
        self.stdout.write('\nCriando estudantes mock...')
        
        estudantes_data = [
            {
                'cpf': '11111111111',
                'nome_completo': 'Maria Silva Santos',
                'idade': 20,
                'matricula': '2023101001',
                'campus': 'Recife',
                'curso': 'Análise e Desenvolvimento de Sistemas',
                'turno': 'NOTURNO',
                'periodo': '3º',
                'email_institucional': '2023101001@estudante.ifpe.edu.br',
            },
            {
                'cpf': '22222222222',
                'nome_completo': 'João Pedro Oliveira',
                'idade': 19,
                'matricula': '2023101002',
                'campus': 'Olinda',
                'curso': 'Ciência da Computação',
                'turno': 'MATUTINO',
                'periodo': '2º',
                'email_institucional': '2023101002@estudante.ifpe.edu.br',
            },
            {
                'cpf': '33333333333',
                'nome_completo': 'Ana Carolina Ferreira',
                'idade': 21,
                'matricula': '2022101003',
                'campus': 'Recife',
                'curso': 'Engenharia de Software',
                'turno': 'VESPERTINO',
                'periodo': '5º',
                'email_institucional': '2022101003@estudante.ifpe.edu.br',
            },
            {
                'cpf': '44444444444',
                'nome_completo': 'Carlos Eduardo Lima',
                'idade': 18,
                'matricula': '2024101004',
                'campus': 'Caruaru',
                'curso': 'Sistemas para Internet',
                'turno': 'NOTURNO',
                'periodo': '1º',
                'email_institucional': '2024101004@estudante.ifpe.edu.br',
            },
            {
                'cpf': '55555555555',
                'nome_completo': 'Fernanda Costa Alves',
                'idade': 22,
                'matricula': '2021101005',
                'campus': 'Recife',
                'curso': 'Análise e Desenvolvimento de Sistemas',
                'turno': 'MATUTINO',
                'periodo': '7º',
                'email_institucional': '2021101005@estudante.ifpe.edu.br',
            },
        ]
        
        for estudante_data in estudantes_data:
            estudante, created = Estudante.objects.get_or_create(
                cpf=estudante_data['cpf'],
                defaults=estudante_data
            )
            if created:
                # Criar endereço para o estudante
                Endereco.objects.get_or_create(
                    estudante=estudante,
                    defaults={
                        'cep': '50000-000',
                        'bairro': 'Centro',
                        'cidade': 'Recife',
                        'estado': 'PE',
                        'telefone_celular': '81999999999',
                    }
                )
                self.stdout.write(f'Estudante criado: {estudante.nome_completo}')
            else:
                self.stdout.write(f'Estudante já existe: {estudante.nome_completo}')
        
        # Criar inscrições mock para o edital 1
        self.stdout.write('\nCriando inscrições (submissões)...')
        
        estudantes = Estudante.objects.all()
        status_options = ['SUBMETIDA', 'EM_ANALISE', 'DEFERIDA', 'INDEFERIDA']
        classificacao_options = ['ANALISE', 'COM_PENDENCIA', 'REGULARIZADO', 'ELEGIVEL', 'NAO_ELEGIVEL', 'CONTEMPLADO', 'NAO_CONTEMPLADO']
        
        for i, estudante in enumerate(estudantes[:5]):
            inscricao, created = Inscricao.objects.get_or_create(
                edital=edital1,
                estudante=estudante,
                defaults={
                    'status': status_options[i % len(status_options)],
                    'classificacao': classificacao_options[i % len(classificacao_options)],
                    'submetida_em': agora - timedelta(days=i*2),
                    'informacoes_estudante': {
                        'nome': estudante.nome_completo,
                        'cpf': estudante.cpf,
                        'matricula': estudante.matricula,
                    },
                    'informacoes_endereco': {
                        'cidade': 'Recife',
                        'estado': 'PE',
                    },
                }
            )
            if created:
                self.stdout.write(f'Inscrição criada: {estudante.nome_completo} - {edital1.numero}')
            else:
                self.stdout.write(f'Inscrição já existe: {estudante.nome_completo} - {edital1.numero}')
        
        self.stdout.write(self.style.SUCCESS('\nDados mock criados com sucesso!'))
        self.stdout.write(self.style.WARNING('\nCredenciais do Pedagogo:'))
        self.stdout.write('  Username: pedagogo')
        self.stdout.write('  Senha: pedagogo123')
        self.stdout.write(self.style.SUCCESS('\nAcesse: http://localhost:8000/login/'))
