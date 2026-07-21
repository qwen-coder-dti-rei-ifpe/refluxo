
python manage.py makemigrations core
python manage.py migrate 
python manage.py popular_dados_mock || {
    echo "Aviso: Não foi possível executar popular_dados_mock"
    echo "No Vercel, isso funcionará corretamente."
    exit 0
}
