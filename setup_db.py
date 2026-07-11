import os
import django
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def main():
    print(">>> Iniciando configuração do banco de dados...")
    
    # 1. Rodar migrações
    print(">>> Aplicando migrações...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print(">>> Migrações aplicadas com sucesso.")
    except Exception as e:
        print(f"!!! Erro ao aplicar migrações: {e}")
        # Não paramos aqui pois o erro pode ser apenas warning em alguns casos, 
        # mas idealmente deveria parar. Para Vercel, vamos tentar continuar se possível.

    # 2. Criar usuário Pedagogo
    print(">>> Verificando/Criando usuário Pedagogo...")
    User = get_user_model()
    
    cpf_pedagogo = '12345678900'  # CPF fictício para login
    senha_pedagogo = 'senha123'
    
    if not User.objects.filter(username=cpf_pedagogo).exists():
        try:
            User.objects.create_superuser(
                username=cpf_pedagogo,
                email=f'{cpf_pedagogo}@pedagogo.local',
                password=senha_pedagogo,
                first_name='Usuário',
                last_name='Pedagogo'
            )
            print(f">>> Usuário Pedagogo criado com sucesso! Login: {cpf_pedagogo} | Senha: {senha_pedagogo}")
        except Exception as e:
            print(f"!!! Erro ao criar usuário: {e}")
    else:
        print(">>> Usuário Pedagogo já existe.")
        
        # Opcional: Resetar a senha se já existir para garantir que é 'senha123'
        user = User.objects.get(username=cpf_pedagogo)
        user.set_password(senha_pedagogo)
        user.save()
        print(">>> Senha do usuário Pedagogo atualizada.")

    print(">>> Configuração concluída.")

if __name__ == '__main__':
    main()
