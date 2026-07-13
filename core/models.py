"""
Models do app core - Modelos de Usuario, Estudante e Endereço.

Este módulo contém os modelos fundamentais para o sistema de inscrições,
incluindo usuário personalizado, dados do estudante e informações de endereço.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """
    Modelo de usuário personalizado para autenticação no sistema.
    Estende o usuário padrão do Django com campos adicionais se necessário.
    """
    # Campos adicionais podem ser adicionados aqui conforme necessidade
    cpf = models.CharField(max_length=14, blank=True, unique=True, verbose_name="CPF")
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.username or self.email


class Estudante(models.Model):
    """
    Modelo que armazena todas as informações pessoais e acadêmicas do estudante.
    Inclui dados cadastrais, informações do curso e documentos.
    """
    # Dados pessoais básicos
    nome_completo = models.CharField(max_length=255, verbose_name="Nome completo")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    idade = models.IntegerField(validators=[MinValueValidator(0)], verbose_name="Idade")
    identidade = models.CharField(max_length=20, blank=True, verbose_name="Identidade (RG)")
    
    # Dados demográficos
    raca = models.CharField(
        max_length=20,
        choices=[
            ('BRANCA', 'Branca'),
            ('PRETA', 'Preta'),
            ('PARDA', 'Parda'),
            ('AMARELA', 'Amarela'),
            ('INDIGENA', 'Indígena'),
        ],
        blank=True,
        verbose_name="Raça"
    )
    cor = models.CharField(max_length=20, blank=True, verbose_name="Cor")
    sexo = models.CharField(
        max_length=10,
        choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')],
        blank=True,
        verbose_name="Sexo"
    )
    orientacao_sexual = models.CharField(max_length=50, blank=True, verbose_name="Orientação sexual")
    genero = models.CharField(max_length=50, blank=True, verbose_name="Gênero")
    
    # Dados acadêmicos
    matricula = models.CharField(max_length=50, unique=True, verbose_name="Matrícula")
    campus = models.CharField(max_length=100, verbose_name="Campus")
    curso = models.CharField(max_length=200, verbose_name="Curso")
    turno = models.CharField(
        max_length=20,
        choices=[('MATUTINO', 'Matutino'), ('VESPERTINO', 'Vespertino'), ('NOTURNO', 'Noturno'), ('INTEGRAL', 'Integral')],
        verbose_name="Turno"
    )
    periodo = models.CharField(max_length=20, verbose_name="Período")
    quantidade_disciplinas = models.IntegerField(default=0, verbose_name="Quantidade de disciplinas")
    origem_escolar = models.CharField(max_length=100, blank=True, verbose_name="Origem escolar")
    eh_cotista = models.BooleanField(default=False, verbose_name="É cotista")
    moradia_estudantil = models.BooleanField(default=False, verbose_name="Moradia estudantil")
    
    # Contato
    email_institucional = models.EmailField(verbose_name="Email institucional")
    
    # Dados bancários
    tipo_conta = models.CharField(
        max_length=20,
        choices=[('CORRENTE', 'Corrente'), ('POUPANCA', 'Poupança')],
        blank=True,
        verbose_name="Tipo de conta"
    )
    numero_agencia = models.CharField(max_length=10, blank=True, verbose_name="Número da agência")
    numero_conta = models.CharField(max_length=20, blank=True, verbose_name="Número da conta")
    banco = models.CharField(max_length=100, blank=True, verbose_name="Banco")
    
    # Documentos (uploads)
    identidade_cpf_anexo = models.FileField(upload_to='documentos/identidade_cpf/', blank=True, null=True, verbose_name="CPF/RG anexo")
    identidade_frente = models.FileField(upload_to='documentos/identidade/frente/', blank=True, null=True, verbose_name="Identidade frente")
    identidade_verso = models.FileField(upload_to='documentos/identidade/verso/', blank=True, null=True, verbose_name="Identidade verso")
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Estudante"
        verbose_name_plural = "Estudantes"
        ordering = ['nome_completo']
    
    def __str__(self):
        return f"{self.nome_completo} ({self.matricula})"


class Endereco(models.Model):
    """
    Modelo que armazena informações de endereço residencial do estudante.
    Inclui dados de localização, condições de moradia e contatos de referência.
    """
    # Vinculação com estudante
    estudante = models.OneToOneField(
        Estudante, 
        on_delete=models.CASCADE, 
        related_name='endereco',
        verbose_name="Estudante"
    )
    
    # Dados de localização
    cep = models.CharField(max_length=9, verbose_name="CEP")
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado")
    ponto_referencia = models.TextField(blank=True, verbose_name="Ponto de referência")
    
    # Informações de visita
    horario_visita = models.CharField(max_length=100, blank=True, verbose_name="Horário de visita")
    telefone_celular = models.CharField(max_length=15, verbose_name="Telefone celular")
    procurar_por_pessoa = models.CharField(max_length=200, blank=True, verbose_name="Procurar por pessoa que more no endereço")
    com_que_mora = models.CharField(max_length=200, blank=True, verbose_name="Com quem mora")
    
    # Condições de moradia
    condicoes_moradia_familiar = models.TextField(blank=True, verbose_name="Condições de moradia familiar")
    regiao_moradia = models.CharField(
        max_length=50,
        choices=[
            ('URBANA', 'Urbana'),
            ('RURAL', 'Rural'),
            ('PERIFERIA', 'Periferia'),
            ('CENTRO', 'Centro'),
        ],
        blank=True,
        verbose_name="Região da moradia"
    )
    abastecimento_agua = models.CharField(max_length=100, blank=True, verbose_name="Abastecimento de água")
    material_construcao = models.CharField(max_length=100, blank=True, verbose_name="Material de construção")
    saneamento = models.CharField(max_length=100, blank=True, verbose_name="Saneamento")
    
    # Contato de referência
    contato_referencia_nome = models.CharField(max_length=200, blank=True, verbose_name="Contato de referência - Nome")
    contato_referencia_telefone = models.CharField(max_length=15, blank=True, verbose_name="Contato de referência - Telefone")
    
    # Mudança para estudar
    mudou_endereco_para_estudar = models.BooleanField(default=False, verbose_name="Mudou do endereço para estudar no IFPE")
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
    
    def __str__(self):
        return f"{self.estudante.nome_completo} - {self.cidade}/{self.estado}"
