"""
Models do aplicativo Family - Modelo de Familiar e Endereço
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Address(models.Model):
    """
    Modelo de Endereço residencial do estudante.
    Contém informações completas sobre a moradia familiar.
    """
    
    # Choices para campos de seleção
    REGIAO_MORADIA_CHOICES = [
        ('URBANA', 'Urbana'),
        ('RURAL', 'Rural'),
    ]
    
    ABASTECIMENTO_AGUA_CHOICES = [
        ('REDE_GERAL', 'Rede geral de distribuição'),
        ('POCO_ARTESIANO', 'Poço artesiano'),
        ('CACIMBA', 'Cacimba'),
        ('RIO_LAGOA', 'Rio ou lagoa'),
        ('OUTRO', 'Outro'),
    ]
    
    MATERIAL_CONSTRUCAO_CHOICES = [
        ('ALVENARIA', 'Alvenaria/tijolo'),
        ('MADEIRA', 'Madeira'),
        ('MISTA', 'Mista (alvenaria e madeira)'),
        ('TAIPA', 'Taipa'),
        ('OUTRO', 'Outro'),
    ]
    
    SANEAMENTO_CHOICES = [
        ('REDE_GERAL', 'Rede geral de esgoto'),
        ('FOSSA_SEPTICA', 'Fossa séptica'),
        ('FOSSA_RUDIMENTAR', 'Fossa rudimentar'),
        ('A_CEU_ABERTO', 'A céu aberto'),
        ('OUTRO', 'Outro'),
    ]
    
    CONDICOES_MORADIA_CHOICES = [
        ('PROPRIA', 'Própria'),
        ('ALUGADA', 'Alugada'),
        ('CEDIDA', 'Cedida'),
        ('OCUPACAO', 'Ocupação'),
    ]
    
    # Relacionamento com estudante (será definido no enrollment)
    # student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='addresses')
    
    # Endereço básico
    cep = models.CharField(_('CEP'), max_length=10)
    bairro = models.CharField(_('Bairro'), max_length=100)
    cidade = models.CharField(_('Cidade'), max_length=100)
    estado = models.CharField(_('Estado'), max_length=2)
    endereco_completo = models.TextField(_('Endereço completo'), null=True, blank=True)
    ponto_referencia = models.CharField(_('Ponto de referência'), max_length=255, null=True, blank=True)
    horario_visita = models.CharField(_('Horário de visita'), max_length=100, null=True, blank=True)
    
    # Informações da moradia
    telefone_celular = models.CharField(_('Telefone celular'), max_length=20, null=True, blank=True)
    procurar_pessoa = models.CharField(
        _('Procurar por pessoa que more no endereço'), 
        max_length=255, 
        null=True, 
        blank=True
    )
    com_que_mora = models.CharField(_('Com que você mora'), max_length=255, null=True, blank=True)
    condicoes_moradia = models.CharField(
        _('Condições de moradia familiar'), 
        max_length=20, 
        choices=CONDICOES_MORADIA_CHOICES,
        null=True, 
        blank=True
    )
    regiao_moradia = models.CharField(
        _('Região da moradia'), 
        max_length=20, 
        choices=REGIAO_MORADIA_CHOICES,
        null=True, 
        blank=True
    )
    abastecimento_agua = models.CharField(
        _('Abastecimento de água'), 
        max_length=30, 
        choices=ABASTECIMENTO_AGUA_CHOICES,
        null=True, 
        blank=True
    )
    material_construcao = models.CharField(
        _('Material de construção'), 
        max_length=30, 
        choices=MATERIAL_CONSTRUCAO_CHOICES,
        null=True, 
        blank=True
    )
    saneamento = models.CharField(
        _('Saneamento'), 
        max_length=30, 
        choices=SANEAMENTO_CHOICES,
        null=True, 
        blank=True
    )
    
    # Contato de referência
    contato_referencia_nome = models.CharField(
        _('Contato de referência - Nome'), 
        max_length=255, 
        null=True, 
        blank=True
    )
    contato_referencia_telefone = models.CharField(
        _('Contato de referência - Telefone'), 
        max_length=20, 
        null=True, 
        blank=True
    )
    
    # Mudança para estudar
    mudou_endereco_estudar = models.BooleanField(
        _('Mudou do endereço para estudar no IFPE?'), 
        default=False
    )
    endereco_anterior = models.TextField(
        _('Endereço anterior'), 
        null=True, 
        blank=True
    )
    
    # Timestamps
    criado_em = models.DateTimeField(_('Criado em'), auto_now_add=True)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Endereço')
        verbose_name_plural = _('Endereços')
        ordering = ['cidade', 'bairro']
    
    def __str__(self):
        return f"{self.cidade} - {self.bairro}"


class FamilyMember(models.Model):
    """
    Modelo de Membro Familiar do grupo familiar do estudante.
    Contém informações pessoais, escolares, de saúde e renda.
    """
    
    # Choices para campos de seleção
    ESTADO_CIVIL_CHOICES = [
        ('SOLTEIRO', 'Solteiro(a)'),
        ('CASADO', 'Casado(a)'),
        ('DIVORCIADO', 'Divorciado(a)'),
        ('VIUVO', 'Viúvo(a)'),
        ('UNIAO_ESTAVEL', 'União estável'),
    ]
    
    GRAU_PARENTESCO_CHOICES = [
        ('PAI', 'Pai'),
        ('MAE', 'Mãe'),
        ('IRMAO', 'Irmão(ã)'),
        ('AVO', 'Avô/Avó'),
        ('TIO', 'Tio(a)'),
        ('PRIMO', 'Primo(a)'),
        ('FILHO', 'Filho(a)'),
        ('CONJUGE', 'Cônjuge'),
        ('OUTRO', 'Outro'),
    ]
    
    ESCOLARIDADE_CHOICES = [
        ('ANALFABETO', 'Analfabeto'),
        ('FUNDAMENTAL_INCOMPLETO', 'Ensino Fundamental incompleto'),
        ('FUNDAMENTAL_COMPLETO', 'Ensino Fundamental completo'),
        ('MEDIO_INCOMPLETO', 'Ensino Médio incompleto'),
        ('MEDIO_COMPLETO', 'Ensino Médio completo'),
        ('SUPERIOR_INCOMPLETO', 'Ensino Superior incompleto'),
        ('SUPERIOR_COMPLETO', 'Ensino Superior completo'),
        ('POS_GRADUACAO', 'Pós-graduação'),
    ]
    
    VINCULO_EMPREGATICIO_CHOICES = [
        ('CLT', 'CLT (Carteira assinada)'),
        ('AUTONOMO', 'Autônomo'),
        ('EMPRESARIO', 'Empresário'),
        ('DESEMPREGADO', 'Desempregado'),
        ('ESTUDANTE', 'Estudante'),
        ('APOSENTADO', 'Aposentado'),
        ('PENSIONISTA', 'Pensionista'),
        ('OUTRO', 'Outro'),
    ]
    
    # Relacionamento com estudante
    student = models.ForeignKey(
        'students.Student', 
        on_delete=models.CASCADE, 
        related_name='family_members',
        null=True,
        blank=True
    )
    
    # Informações pessoais
    data_nascimento = models.DateField(_('Data de nascimento'))
    idade = models.PositiveIntegerField(_('Idade'))
    cpf = models.CharField(_('CPF'), max_length=14)
    nome = models.CharField(_('Nome'), max_length=255)
    inscricao = models.CharField(_('Inscrição'), max_length=50, null=True, blank=True)
    grau_parentesco = models.CharField(
        _('Grau de parentesco'), 
        max_length=30, 
        choices=GRAU_PARENTESCO_CHOICES
    )
    estado_civil = models.CharField(
        _('Estado civil'), 
        max_length=20, 
        choices=ESTADO_CIVIL_CHOICES,
        null=True, 
        blank=True
    )
    
    # Documento anexo
    cpf_anexo = models.FileField(
        _('CPF Anexo'), 
        upload_to='documents/family/', 
        null=True, 
        blank=True
    )
    
    # Escolaridade e saúde
    escolaridade = models.CharField(
        _('Escolaridade'), 
        max_length=40, 
        choices=ESCOLARIDADE_CHOICES,
        null=True, 
        blank=True
    )
    possui_agravo_saude = models.BooleanField(_('Possui agravo de saúde?'), default=False)
    descricao_agravo = models.TextField(
        _('Descrição do agravo'), 
        null=True, 
        blank=True
    )
    possui_necessidade_especifica = models.BooleanField(
        _('Possui necessidade específica?'), 
        default=False
    )
    descricao_necessidade = models.TextField(
        _('Descrição da necessidade'), 
        null=True, 
        blank=True
    )
    
    # Situação profissional e renda
    vinculo_empregaticio = models.CharField(
        _('Vínculo empregatício'), 
        max_length=30, 
        choices=VINCULO_EMPREGATICIO_CHOICES,
        null=True, 
        blank=True
    )
    rendimento_mensal = models.DecimalField(
        _('Rendimento mensal (R$)'), 
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )
    recebe_pensao = models.BooleanField(_('Recebe pensão?'), default=False)
    valor_pensao = models.DecimalField(
        _('Valor da pensão (R$)'), 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Timestamps
    criado_em = models.DateTimeField(_('Criado em'), auto_now_add=True)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Membro Familiar')
        verbose_name_plural = _('Membros Familiares')
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.grau_parentesco})"
    
    def save(self, *args, **kwargs):
        """Calcula automaticamente a idade ao salvar."""
        from datetime import date
        if self.data_nascimento and not self.idade:
            hoje = date.today()
            self.idade = hoje.year - self.data_nascimento.year - (
                (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        super().save(*args, **kwargs)
