# IFPE MVP - Sistema de Apoio e Manutenção Acadêmica

Sistema web e API para gestão do programa de apoio e manutenção acadêmica do IFPE.

## Funcionalidades

- **Consulta por matrícula/CPF**: Auto-preenchimento de formulários com dados das APIs QAcadêmico e ConectaGov
- **5 Eixos de informações**: Estudante, Endereço, Familiares, Deslocamento, Inscrição
- **Gestão de Editais**: Abertura e fechamento de períodos de inscrição
- **Dashboard do Estudante**: Acompanhamento de inscrições e status
- **Análise de Elegibilidade**: Avaliação por pedagogos com critérios de renda per capita e benefícios sociais

## Stack Tecnológica

- Backend: Python 3.12 + Django 6.0 + Django REST Framework
- Banco de Dados: PostgreSQL 15
- Integrações: QAcadêmico, ConectaGov (CBC/CadÚnico) - mocks para desenvolvimento
- Documentação: Swagger/OpenAPI
- Infraestrutura: Docker, Docker Compose
- CI/CD: GitLab CI

## Instalação Local

### Opção 1: Docker Compose (Recomendado)

```bash
docker-compose up -d
```

Acesse: http://localhost:8000

### Opção 2: Desenvolvimento Local

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env

# Rodar migrações
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

## API Endpoints

- **Swagger Docs**: http://localhost:8000/api/docs/
- **Admin Django**: http://localhost:8000/admin/

### Principais Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/core/estudantes/` | GET, POST | Listar/criar estudantes |
| `/api/integrations/qacademico/consultar/` | GET | Consultar dados QAcadêmico |
| `/api/integrations/conecta-gov/consultar/` | GET | Consultar dados ConectaGov |
| `/api/integrations/consulta-elegibilidade/` | GET | Verificar elegibilidade |
| `/api/inscricoes/editais/` | GET, POST | Gerenciar editais |
| `/api/inscricoes/inscricoes/` | GET, POST | Gerenciar inscrições |
| `/api/inscricoes/dashboard/<cpf>/` | GET | Dashboard do estudante |

## Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```env
SECRET_KEY=sua-chave-secreta
DEBUG=True
DB_NAME=ifpe_mvp
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

## Testes

```bash
pytest
```

## Deploy

### Vercel/Netlify (Frontend estático)

Para deploy do frontend em Vercel/Netlify, exporte os arquivos estáticos:

```bash
python manage.py collectstatic
```

Configure o build command e publish directory na plataforma escolhida.

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Estrutura do Projeto

```
/workspace
├── config/          # Configurações Django
├── core/            # Models Estudante e Endereco
├── integrations/    # Integrações QAcadêmico e ConectaGov
├── inscricoes/      # Gestão de editais e inscrições
├── templates/       # Templates HTML
├── static/          # Arquivos estáticos
├── media/           # Uploads de arquivos
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Licença

MIT
