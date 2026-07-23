"""
Serviço de integração com API QAcadêmico (Mock Postman).

Este módulo fornece funções para consultar dados do estudante
através da API mock do QAcadêmico hospedada no Postman.
"""
import requests
from django.conf import settings


# URL base da API Mock do Postman
QACADEMICO_MOCK_BASE_URL = "https://50e37893-2fc7-4825-94e8-0397f4267d24.mock.pstmn.io"


class QAcademicoAPIService:
    """
    Serviço para integração com a API do QAcadêmico (Mock Postman).
    
    Fornece métodos para buscar dados do estudante pela matrícula
    e mapear a resposta para o formato utilizado pelo sistema.
    """
    
    BASE_URL = QACADEMICO_MOCK_BASE_URL
    
    @classmethod
    def buscar_estudante_por_matricula(cls, matricula):
        """
        Busca dados do estudante pela matrícula na API do QAcadêmico.
        
        Args:
            matricula (str): Número da matrícula do estudante.
            
        Returns:
            dict: Dados do estudante mapeados para o formato do sistema,
                  ou None se não encontrado ou erro na API.
            str: Mensagem de erro caso ocorra algum problema.
        """
        if not matricula:
            return None, "Matrícula é obrigatória"
        
        url = f"{cls.BASE_URL}/qacademico/student/{matricula}"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                dados_api = response.json()
                dados_mapeados = cls._mapear_resposta_api(dados_api)
                return dados_mapeados, None
            elif response.status_code == 404:
                return None, "Matrícula não encontrada na base do QAcadêmico"
            else:
                return None, f"Erro ao consultar API QAcadêmico: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return None, "Erro de conexão com a API QAcadêmico"
        except requests.exceptions.Timeout:
            return None, "Tempo de espera excedido ao consultar API QAcadêmico"
        except requests.exceptions.RequestException as e:
            return None, f"Erro ao consultar API QAcadêmico: {str(e)}"
        except Exception as e:
            return None, f"Erro inesperado: {str(e)}"
    
    @classmethod
    def _mapear_resposta_api(cls, dados_api):
        """
        Mapeia a resposta da API do QAcadêmico para o formato utilizado pelo sistema.
        
        A API retorna os seguintes campos:
        {
            "enrollmentId": 257352,
            "campusId": 1,
            "courseSyllabusId": 3492,
            "enrollment": "20241001",
            "enrollmentStatus": "Abandono/Evasão",
            "enrollmentStatusCode": 9,
            "fullName": "Nascimento Costa Cesar Caio",
            "socialName": null,
            "motherName": "Barbosa Costa Josecarmem",
            "brCPF": "161.711.994-42",
            "email": "test@gmail.com",
            "gender": "M",
            "race": "PAR",
            "numberOfChildren": 0,
            "shift": "V",
            "currentPeriod": 1,
            "brRG": "1442186",
            "maritalStatus": "SOLTEIRO (A)",
            "fatherName": "José Roberval Nascimento",
            "quota": "Aluno de Escola Pública com renda > 1,5 SM por pessoa, autodeclarado preto, pardo ou indígena",
            "birthday": "2004-02-03",
            "campusName": "IFPE - CAMPUS RECIFE",
            "courseName": "TÉCNICO EM QUÍMICA SUB - RC (2014/2)",
            "initialYear": 2023,
            "initialSemester": 2,
            "endYear": 2024,
            "endSemester": 1,
            "courseLevel": "Técnico",
            "standardizedCourse": "TÉCNICO EM QUÍMICA",
            "gradePointAverage": 0.0
        }
        
        Returns:
            dict: Dados mapeados no formato esperado pelo sistema.
        """
        if not dados_api:
            return {}
        
        # Mapeamento de turnos (shift)
        turno_map = {
            'M': 'MATUTINO',
            'V': 'VESPERTINO',
            'N': 'NOTURNO',
            'I': 'INTEGRAL',
        }
        
        # Mapeamento de gênero/sexo
        sexo_map = {
            'M': 'MASCULINO',
            'F': 'FEMININO',
            'O': 'OUTRO',
        }
        
        # Mapeamento de raça/cor
        race_map = {
            'BRANCO': 'BRANCA',
            'PRETO': 'PRETA',
            'PAR': 'PARDA',
            'PARDO': 'PARDA',
            'AMARELO': 'AMARELA',
            'INDIGENA': 'INDIGENA',
            'INDÍGENA': 'INDIGENA',
        }
        
        # Extrair e limpar CPF (remover pontos e traços)
        cpf_raw = dados_api.get('brCPF', '')
        cpf_limpo = ''.join(filter(str.isdigit, cpf_raw)) if cpf_raw else ''
        
        # Extrair e limpar RG
        rg_raw = dados_api.get('brRG', '')
        
        # Calcular idade a partir da data de nascimento
        idade = None
        birthday = dados_api.get('birthday')
        if birthday:
            try:
                from datetime import date
                birth_date = date.fromisoformat(birthday)
                today = date.today()
                idade = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            except (ValueError, TypeError):
                idade = None
        
        # Obter turno mapeado
        shift_raw = dados_api.get('shift', '')
        turno = turno_map.get(shift_raw, shift_raw)
        
        # Obter sexo mapeado
        gender_raw = dados_api.get('gender', '')
        sexo = sexo_map.get(gender_raw, gender_raw)
        
        # Obter raça mapeada
        race_raw = dados_api.get('race', '')
        raca = race_map.get(race_raw.upper(), race_raw)
        
        # Obter nome do curso padronizado
        course_name = dados_api.get('standardizedCourse') or dados_api.get('courseName', '')
        
        # Obter campus
        campus_name = dados_api.get('campusName', '')
        
        # Obter período atual
        current_period = dados_api.get('currentPeriod', 0)
        periodo = f"{current_period}º" if current_period else ""
        
        # Verificar se é cotista baseado na quota
        quota = dados_api.get('quota', '')
        eh_cotista = bool(quota) and quota.lower() not in ['não', 'nao', 'none', '']
        
        # Montar dados mapeados
        dados_mapeados = {
            'nome_completo': dados_api.get('fullName', ''),
            'cpf': cpf_limpo,
            'identidade': rg_raw,
            'data_nascimento': birthday,
            'idade': idade,
            'raca': raca,
            'sexo': sexo,
            'genero': sexo,  # Gênero igual ao sexo por padrão
            'matricula': dados_api.get('enrollment', ''),
            'campus': campus_name,
            'curso': course_name,
            'turno': turno,
            'periodo': periodo,
            'eh_cotista': eh_cotista,
            'quota_info': quota,
            'email': dados_api.get('email', ''),
            'email_institucional': dados_api.get('email', ''),
            'email_pessoal': dados_api.get('email', ''),
            'nome_mae': dados_api.get('motherName', ''),
            'nome_pai': dados_api.get('fatherName', ''),
            'estado_civil': dados_api.get('maritalStatus', ''),
            'numero_filhos': dados_api.get('numberOfChildren', 0),
            'status_matricula': dados_api.get('enrollmentStatus', ''),
            'nivel_curso': dados_api.get('courseLevel', ''),
            'media_geral': dados_api.get('gradePointAverage', 0.0),
            'ano_inicio': dados_api.get('initialYear'),
            'semestre_inicio': dados_api.get('initialSemester'),
            'ano_fim': dados_api.get('endYear'),
            'semestre_fim': dados_api.get('endSemester'),
        }
        
        return dados_mapeados


def buscar_estudante_qacademico(matricula):
    """
    Função utilitária para buscar estudante pela matrícula.
    
    Args:
        matricula (str): Número da matrícula do estudante.
        
    Returns:
        tuple: (dados_mapeados, mensagem_erro)
               dados_mapeados será None se houver erro.
               mensagem_erro será None se sucesso.
    """
    return QAcademicoAPIService.buscar_estudante_por_matricula(matricula)
