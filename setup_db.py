"""
Script de configuração do banco de dados para Vercel.

Este script é executado durante o build no Vercel para:
1. Criar migrations se necessário
2. Aplicar migrations
3. Criar usuário de demonstração (12345678900 / 123) com permissões de staff
"""
import os
import django

# Configura o módulo de configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def setup_database():
    """Configura o banco de dados e cria usuário de demonstração."""
    User = get_user_model()
    
    # Dados do usuário de demonstração
    username = '12345678900'
    password = '123'
    
    # Verifica se o usuário já existe
    if User.objects.filter(username=username).exists():
        print(f"Usuário '{username}' já existe. Atualizando senha...")
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"Senha do usuário '{username}' atualizada com sucesso.")
    else:
        print(f"Criando usuário '{username}' com permissões de administrador...")
        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=True,
            is_superuser=True,
        )
        print(f"Usuário '{username}' criado com sucesso!")
    
    print("\n=== Configuração concluída ===")
    print(f"Login: {username}")
    print(f"Senha: {password}")
    print("Acesse /admin/ ou /login/ para testar.")

if __name__ == '__main__':
    setup_database()
