from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Cria usuários de teste para pedagogo e controlador'

    def handle(self, *args, **options):
        # Criar grupos se não existirem
        grupo_pedagogo, _ = Group.objects.get_or_create(name='Pedagogo')
        grupo_controlador, _ = Group.objects.get_or_create(name='Controlador')
        
        # Criar usuário Pedagogo
        if not User.objects.filter(username='pedagogo').exists():
            pedagogo = User.objects.create_user(
                username='pedagogo',
                password='senha123',
                email='pedagogo@ifpe.edu.br',
                first_name='Pedagogo',
                last_name='Teste'
            )
            pedagogo.groups.add(grupo_pedagogo)
            pedagogo.is_staff = True
            pedagogo.save()
            self.stdout.write(self.style.SUCCESS('Usuário "pedagogo" criado com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING('Usuário "pedagogo" já existe.'))
        
        # Criar usuário Controlador
        if not User.objects.filter(username='controlador').exists():
            controlador = User.objects.create_user(
                username='controlador',
                password='senha123',
                email='controlador@ifpe.edu.br',
                first_name='Controlador',
                last_name='Teste'
            )
            controlador.groups.add(grupo_controlador)
            controlador.is_staff = True
            controlador.save()
            self.stdout.write(self.style.SUCCESS('Usuário "controlador" criado com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING('Usuário "controlador" já existe.'))
        
        self.stdout.write(self.style.SUCCESS('\n=== CREDENCIAIS DE TESTE ==='))
        self.stdout.write('Pedagogo: usuário=pedagogo, senha=senha123')
        self.stdout.write('Controlador: usuário=controlador, senha=senha123')
        self.stdout.write('===========================\n')
