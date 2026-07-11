"""
Models do aplicativo Students - Modelo de Estudante com todos os campos necessários
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Student(models.Model):
    """
    Modelo de Estudante com informações completas para o programa de apoio acadêmico.
    Inclui dados pessoais, acadêmicos e bancários.
    """
    
    # Choices para campos de seleção
    RACA_CHOICES = [
        ('BRANCA', 'Branca'),
        ('PRETA', 'Preta'),
        ('PARDA', 'Parda'),
        ('AMARELA', 'Amarela'),
        ('INDIGENA', 'Indígena'),
    ]
    
    GENERO_CHOICES = [
        ('MASCULINO', 'Masculino'),
        ('FEMININO', 'Feminino'),
        ('NAO_BINARIO', 'Não-binário'),
        ('OUTRO', 'Outro'),
    ]
    
    ORIENTACAO_SEXUAL_CHOICES = [
        ('HETEROSSEXUAL', 'Heterossexual'),
        ('HOMOSSEXUAL', 'Homossexual'),
        ('BISSEXUAL', 'Bissexual'),
        ('ASSEXUAL', 'Assexual'),
        ('OUTRO', 'Outro'),
        ('NAO_DECLARADA', 'Prefiro não declarar'),
    ]
    
    TURNO_CHOICES = [
        ('MATUTINO', 'Matutino'),
        ('VESPERTINO', 'Vespertino'),
        ('NOTURNO', 'Noturno'),
        ('INTEGRAL', 'Integral'),
    ]
    
    ORIGEM_ESCOLAR_CHOICES = [
        ('PUBLICA', 'Escola Pública'),
        ('PRIVADA', 'Escola Privada'),
    ]
    
    TIPO_CONTA_CHOICES = [
        ('CORRENTE', 'Conta Corrente'),
        ('POUPANCA', 'Conta Poupança'),
    ]
    
    BANCO_CHOICES = [
        ('001', 'Banco do Brasil'),
        ('104', 'Caixa Econômica Federal'),
        ('237', 'Bradesco'),
        ('341', 'Itaú'),
        ('033', 'Santander'),
        ('102', 'XP Investimentos'),
        ('OUTRO', 'Outro'),
    ]
    
    # Relacionamento com usuário Django
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='student',
        verbose_name=_('Usuário'),
        null=True, 
        blank=True
    )
    
    # Informações Pessoais Básicas
    nome_completo = models.CharField(_('Nome completo'), max_length=255)
    cpf = models.CharField(_('CPF'), max_length=14, unique=True)
    data_nascimento = models.DateField(_('Data de nascimento'), null=True, blank=True)
    idade = models.PositiveIntegerField(_('Idade'), null=True, blank=True)
    identidade = models.CharField(_('Identidade (RG)'), max_length=20, null=True, blank=True)
    raca = models.CharField(_('Raça'), max_length=20, choices=RACA_CHOICES, null=True, blank=True)
    cor = models.CharField(_('Cor'), max_length=50, null=True, blank=True)
    sexo = models.CharField(_('Sexo'), max_length=20, choices=GENERO_CHOICES, null=True, blank=True)
    orientacao_sexual = models.CharField(
        _('Orientação sexual'), 
        max_length=30, 
        choices=ORIENTACAO_SEXUAL_CHOICES, 
        null=True, 
        blank=True
    )
    genero = models.CharField(_('Gênero'), max_length=50, null=True, blank=True)
    
    # Informações Acadêmicas
    matricula = models.CharField(_('Matrícula'), max_length=50, unique=True)
    campus = models.CharField(_('Campus'), max_length=100, null=True, blank=True)
    curso = models.CharField(_('Curso'), max_length=200, null=True, blank=True)
    turno = models.CharField(_('Turno'), max_length=20, choices=TURNO_CHOICES, null=True, blank=True)
    periodo = models.PositiveIntegerField(_('Período'), null=True, blank=True)
    quantidade_disciplinas = models.PositiveIntegerField(_('Quantidade de disciplinas'), default=0)
    origem_escolar = models.CharField(
        _('Origem escolar'), 
        max_length=20, 
        choices=ORIGEM_ESCOLAR_CHOICES, 
        null=True, 
        blank=True
    )
    eh_cotista = models.BooleanField(_('É cotista?'), default=False)
    moradia_estudantil = models.BooleanField(_('Usa moradia estudantil?'), default=False)
    
    # Contato
    email_institucional = models.EmailField(_('Email institucional'), null=True, blank=True)
    telefone_celular = models.CharField(_('Telefone celular'), max_length=20, null=True, blank=True)
    
    # Informações Bancárias
    tipo_conta = models.CharField(
        _('Tipo de conta'), 
        max_length=20, 
        choices=TIPO_CONTA_CHOICES, 
        null=True, 
        blank=True
    )
    numero_agencia = models.CharField(_('Número da agência'), max_length=10, null=True, blank=True)
    numero_conta = models.CharField(_('Número da conta'), max_length=20, null=True, blank=True)
    banco = models.CharField(_('Banco'), max_length=10, choices=BANCO_CHOICES, null=True, blank=True)
    banco_outro = models.CharField(_('Especificar banco'), max_length=100, null=True, blank=True)
    
    # Documentos Anexos
    identidade_cpf_anexo = models.FileField(
        _('CPF Anexo'), 
        upload_to='documents/identity/', 
        null=True, 
        blank=True
    )
    identidade_frente = models.FileField(
        _('Identidade Frente'), 
        upload_to='documents/identity/', 
        null=True, 
        blank=True
    )
    identidade_verso = models.FileField(
        _('Identidade Verso'), 
        upload_to='documents/identity/', 
        null=True, 
        blank=True
    )
    
    # Timestamps
    criado_em = models.DateTimeField(_('Criado em'), auto_now_add=True)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Estudante')
        verbose_name_plural = _('Estudantes')
        ordering = ['nome_completo']
    
    def __str__(self):
        return f"{self.nome_completo} ({self.matricula})"
    
    def calcular_idade(self):
        """Calcula a idade a partir da data de nascimento."""
        from datetime import date
        if self.data_nascimento:
            hoje = date.today()
            self.idade = hoje.year - self.data_nascimento.year - (
                (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
            self.save(update_fields=['idade'])
