"""
Models do app inscricoes - Modelos para editais, inscrições e análises.

Este módulo contém os modelos para gestão do programa de apoio
e manutenção acadêmica, incluindo editais, inscrições e análises.
"""
from django.db import models
from django.utils import timezone
from core.models import Estudante


class Edital(models.Model):
    """
    Modelo que representa um edital de inscrição para o programa.
    
    Define o período de inscrições, descrição e regras do edital
    para seleção de estudantes beneficiários.
    """
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('SUSPENSO', 'Suspenso'),
        ('CANCELADO', 'Cancelado'),
        ('FINALIZADO', 'Finalizado'),
    ]
    
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    numero = models.CharField(max_length=50, unique=True)
    
    # Período de inscrições dos estudantes
    periodo_inscricao_abertura = models.DateTimeField(null=True, blank=True)
    periodo_inscricao_fechamento = models.DateTimeField(null=True, blank=True)
    
    # Período de avaliação dos pedagogos
    periodo_avaliacao_abertura = models.DateTimeField(null=True, blank=True)
    periodo_avaliacao_fechamento = models.DateTimeField(null=True, blank=True)
    
    # Períodos para recursos (assistente social)
    periodo_recurso_solicitacao_abertura = models.DateTimeField(
        'Período de solicitação de recursos - Abertura', 
        null=True, 
        blank=True,
        help_text='Período para o assistente social solicitar recursos'
    )
    periodo_recurso_solicitacao_fechamento = models.DateTimeField(
        'Período de solicitação de recursos - Fechamento', 
        null=True, 
        blank=True
    )
    
    periodo_resultado_parcial_divulgacao = models.DateTimeField(
        'Período de divulgação do resultado parcial', 
        null=True, 
        blank=True,
        help_text='Data de divulgação do resultado parcial para os estudantes'
    )
    
    periodo_recurso_estudante_submissao_abertura = models.DateTimeField(
        'Período de submissão de recursos pelos estudantes - Abertura', 
        null=True, 
        blank=True,
        help_text='Período para estudantes submeterem recursos após resultado parcial'
    )
    periodo_recurso_estudante_submissao_fechamento = models.DateTimeField(
        'Período de submissão de recursos pelos estudantes - Fechamento', 
        null=True, 
        blank=True
    )
    
    periodo_recurso_avaliacao_abertura = models.DateTimeField(
        'Período de avaliação dos recursos - Abertura', 
        null=True, 
        blank=True,
        help_text='Período para avaliação dos recursos dos estudantes após resultado parcial'
    )
    periodo_recurso_avaliacao_fechamento = models.DateTimeField(
        'Período de avaliação dos recursos - Fechamento', 
        null=True, 
        blank=True
    )
    
    periodo_resultado_final_divulgacao = models.DateTimeField(
        'Período de divulgação do resultado final', 
        null=True, 
        blank=True,
        help_text='Data de divulgação do resultado final'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVO')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Edital"
        verbose_name_plural = "Editais"
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"{self.numero} - {self.titulo}"
    
    def esta_com_inscricoes_abertas(self):
        """Verifica se o edital está com inscrições abertas."""
        agora = timezone.now()
        return (self.ativo and 
                self.status == 'ATIVO' and
                self.periodo_inscricao_abertura and
                self.periodo_inscricao_fechamento and
                self.periodo_inscricao_abertura <= agora <= self.periodo_inscricao_fechamento)
    
    def esta_dentro_periodo_inscricoes(self):
        """Verifica se o edital está ativo e dentro do período de inscrições."""
        agora = timezone.now()
        return (self.ativo and 
                self.status == 'ATIVO' and
                self.periodo_inscricao_abertura and
                self.periodo_inscricao_fechamento and
                self.periodo_inscricao_abertura <= agora <= self.periodo_inscricao_fechamento)
    
    def esta_com_avaliacao_aberta(self):
        """Verifica se o edital está com avaliação aberta."""
        agora = timezone.now()
        return (self.ativo and 
                self.status == 'ATIVO' and
                self.periodo_avaliacao_abertura and
                self.periodo_avaliacao_fechamento and
                self.periodo_avaliacao_abertura <= agora <= self.periodo_avaliacao_fechamento)
    
    def esta_aberto(self):
        """Verifica se o edital está aberto para inscrições."""
        return self.esta_dentro_periodo_inscricoes()


class Inscricao(models.Model):
    """
    Modelo que representa a inscrição de um estudante em um edital.
    
    Contém todos os dados do formulário de inscrição dividido em
    eixos: estudante, endereço, familiares, deslocamento e inscrição.
    """
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('SUBMETIDA', 'Submetida'),
        ('EM_ANALISE', 'Em análise'),
        ('DEFERIDA', 'Deferida'),
        ('INDEFERIDA', 'Indeferida'),
    ]
    
    # Status de classificação da inscrição
    CLASSIFICACAO_CHOICES = [
        ('ANALISE', 'Em Análise'),
        ('COM_PENDENCIA', 'Com Pendência'),
        ('NAO_REGULARIZADO', 'Não Regularizado'),
        ('REGULARIZADO', 'Regularizado'),
        ('NAO_ELEGIVEL', 'Não Elegível'),
        ('ELEGIVEL', 'Elegível'),
        ('CONTEMPLADO', 'Contemplado'),
        ('NAO_CONTEMPLADO', 'Não Contemplado'),
    ]
    
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name='inscricoes')
    estudante = models.ForeignKey(Estudante, on_delete=models.CASCADE, related_name='inscricoes')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RASCUNHO')
    classificacao = models.CharField(max_length=30, choices=CLASSIFICACAO_CHOICES, default='ANALISE')
    
    # Dados do formulário (armazenados como JSON para flexibilidade)
    informacoes_estudante = models.JSONField(default=dict, blank=True)
    informacoes_endereco = models.JSONField(default=dict, blank=True)
    informacoes_familiares = models.JSONField(default=list, blank=True)
    informacoes_deslocamento = models.JSONField(default=dict, blank=True)
    informacoes_inscricao = models.JSONField(default=dict, blank=True)
    
    # Documentos anexados
    documentos = models.JSONField(default=list, blank=True)
    
    # Metadados
    submetida_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"
        unique_together = ['edital', 'estudante']
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"{self.estudante.nome_completo} - {self.edital.numero}"
    
    def pode_editar(self):
        """Verifica se a inscrição ainda pode ser editada."""
        return self.status == 'RASCUNHO' and self.edital.esta_aberto()


class Analise(models.Model):
    """
    Modelo que representa a análise de uma inscrição pelo pedagogo.
    
    Contém a avaliação de elegibilidade, comentários e decisão
    sobre a concessão do benefício.
    """
    inscricao = models.OneToOneField(Inscricao, on_delete=models.CASCADE, related_name='analise')
    pedagogo = models.CharField(max_length=255)  # Em produção seria ForeignKey para User
    data_analise = models.DateTimeField(auto_now_add=True)
    
    # Avaliação
    elegivel = models.BooleanField()
    indice_vulnerabilidade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Decisão
    deferida = models.BooleanField()
    valor_bolsa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    comentario = models.TextField(blank=True)
    
    # Critérios de avaliação
    criterios_avaliacao = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Análise"
        verbose_name_plural = "Análises"
        ordering = ['-data_analise']
    
    def __str__(self):
        return f"Análise de {self.inscricao.estudante.nome_completo} - {'Deferida' if self.deferida else 'Indeferida'}"


class MembroFamiliar(models.Model):
    """
    Modelo opcional para armazenar membros familiares separadamente.
    
    Permite gestão mais detalhada dos familiares do grupo familiar
    do estudante.
    """
    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE, related_name='familiares')
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14)
    data_nascimento = models.DateField()
    parentesco = models.CharField(max_length=50)
    escolaridade = models.CharField(max_length=100, blank=True)
    rendimento_mensal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    possui_agravo_saude = models.BooleanField(default=False)
    possui_necessidade_especifica = models.BooleanField(default=False)
    vinculo_empregaticio = models.CharField(max_length=100, blank=True)
    recebe_pensao = models.BooleanField(default=False)
    imagem_cpf = models.FileField(upload_to='familiares/cpf/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Membro Familiar"
        verbose_name_plural = "Membros Familiares"
    
    def __str__(self):
        return f"{self.nome} - {self.parentesco}"
