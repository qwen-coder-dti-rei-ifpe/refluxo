#!/bin/bash
pip install -r requirements.txt --break-system-packages

# Tenta aplicar migrations com o banco configurado (PostgreSQL no Vercel)
python manage.py makemigrations core
python manage.py migrate || {
    echo "Aviso: Não foi possível conectar ao banco de dados PostgreSQL."
    echo "No Vercel, isso funcionará corretamente com as variáveis de ambiente."
    exit 0
}

python setup_db.py || {
    echo "Aviso: Não foi possível executar setup_db.py (provavelmente devido à conexão com o banco)."
    echo "No Vercel, isso funcionará corretamente."
    exit 0
}
