"""
Configurações do Django para o projeto IFPE MVP.

Este arquivo contém todas as configurações do projeto Django,
incluindo apps instalados, middlewares, banco de dados, etc.
"""
from pathlib import Path
from decouple import config

# Constrói o caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Chave secreta para criptografia e sessões (use variável de ambiente em produção)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

# Modo de debug (desative em produção)
DEBUG = config('DEBUG', default=True, cast=bool)

# Hosts permitidos (configure para seu domínio em produção)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,.vercel.app').split(',')

# Apps do projeto e apps de terceiros instalados
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps de terceiros
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'widget_tweaks',
    
    # Apps do projeto
    'core',
    'integrations',
    'inscricoes',
]

# Middlewares processam requisições e respostas
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuração de URLs
ROOT_URLCONF = 'config.urls'

# Configuração de templates HTML
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Ponto de entrada da aplicação WSGI
WSGI_APPLICATION = 'config.wsgi.application'

# Configuração do banco de dados PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DATABASE', default='postgres'),
        'USER': config('POSTGRES_USER', default='postgres.xeodkrcoekfsonnwcuag'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='Zl6BfAU366Cu9Zoa'),
        'HOST': config('POSTGRES_HOST', default='aws-0-us-east-1.pooler.supabase.com'),
        'PORT': config('POSTGRES_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# URL do banco de dados para compatibilidade com outras ferramentas
DATABASE_URL = config('DATABASE_URL', default='postgres://postgres.xeodkrcoekfsonnwcuag:Zl6BfAU366Cu9Zoa@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require')

# Validação de senhas do Django
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalização (idioma e fuso horário)
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Recife'
USE_I18N = True
USE_TZ = True

# Arquivos estáticos (CSS, JS, imagens)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# Arquivos de mídia (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Chave primária padrão auto campo
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuração do Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# Configuração do Swagger/OpenAPI para documentação
SPECTACULAR_SETTINGS = {
    'TITLE': 'IFPE MVP API',
    'DESCRIPTION': 'API para programa de apoio e manutenção acadêmica do IFPE',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Configuração de CORS para permitir acesso frontend
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL', default=True, cast=bool)
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')

# Configurações de segurança para uploads
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Configuração de Autenticação - Forçar backend padrão no Vercel
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Modelo de usuário personalizado
AUTH_USER_MODEL = 'core.Usuario'

# URL de redirecionamento após login
LOGIN_REDIRECT_URL = 'pedagogo_dashboard'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'
