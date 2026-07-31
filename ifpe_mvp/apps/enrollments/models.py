"""
Models do aplicativo Enrollments - Edital, Inscrição e Deslocamento
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class EnrollmentPeriod(models.Model):
    """
    Modelo de Período de Inscrição (Edital).
    Define o período durante o qual os estudantes podem se inscrever.
    """
    
    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('FECHADO', 'Fechado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    titulo = models.CharField(_('Título do edital'), max_length=255)
    descricao = models.TextField(_('Descrição'))
    data_inicio = models.DateTimeField(_('Data de início'))
    data_fim = models.DateTimeField(_('Data de fim'))
    status = models.CharField(
        _('Status'), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='FECHADO'
    )
    ativo = models.BooleanField(_('Ativo?'), default=False)
    
    # Timestamps
    criado_em = models.DateTimeField(_('Criado em'), auto_now_add=True)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Período de Inscrição')
        verbose_name_plural = _('Períodos de Inscrição')
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.titulo} ({self.data_inicio.strftime('%d/%m/%Y')} - {self.data_fim.strftime('%d/%m/%Y')})"
    
    def esta_aberto(self):
        """Verifica se o período de inscrição está aberto."""
        agora = timezone.now()
        return self.ativo and self.data_inicio <= agora <= self.data_fim


class Displacement(models.Model):
    """
    Modelo de Deslocamento do estudante.
    Contém informações sobre transporte e trajeto diário.
    """
    
    TIPO_TRANSPORTE_CHOICES = [
        ('ONIBUS', 'Ônibus'),
        ('METRO', 'Metrô'),
        ('CARRO', 'Carro próprio'),
        ('MOTO', 'Motocicleta'),
        ('BICICLETA', 'Bicicleta'),
        ('A_PE', 'A pé'),
        ('VAN', 'Van/Kombi'),
        ('OUTRO', 'Outro'),
    ]
    
    # Relacionamento será definido no Enrollment
    # student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    
    valor_mensal_transporte = models.DecimalField(
        _('Valor mensal gasto com transporte (R$)'), 
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )
    trajeto_percorrido = models.TextField(
        _('Trajeto percorrido diariamente'), 
        help_text=_('Descreva o trajeto que você faz diariamente para chegar ao campus')
    )
    tipo_transporte = models.CharField(
        _('Tipo de transporte'), 
        max_length=30, 
        choices=TIPO_TRANSPORTE_CHOICES
    )
    observacoes = models.TextField(_('Observações'), null=True, blank=True)
    
    # Timestamps
    criado_em = models.DateTimeField(_('Criado em'), auto_now_add=True)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Deslocamento')
        verbose_name_plural = _('Deslocamentos')
    
    def __str__(self):
        return f"Transporte: {self.get_tipo_transporte_display()} - R$ {self.valor_mensal_transporte}"


class Enrollment(models.Model):
    """
    Modelo principal de Inscrição no programa de apoio acadêmico.
    Agrega todas as informações do estudante, família, endereço e deslocamento.
    """
    
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('SUBMETIDA', 'Submetida'),
        ('EM_ANALISE', 'Em análise'),
        ('APROVADA', 'Aprovada'),
        ('REPROVADA', 'Reprovada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
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
    
    FAIXA_RENDA_CHOICES = [
        ('ATE_05_SALARIOS', 'Até 0,5 salário mínimo per capita'),
        ('ATE_1_SALARIO', 'Até 1 salário mínimo per capita'),
        ('ATE_15_SALARIOS', 'Até 1,5 salários mínimos per capita'),
        ('ACIMA_15_SALARIOS', 'Acima de 1,5 salários mínimos per capita'),
    ]
    
    ORIGEM_RENDA_CHOICES = [
        ('TRABALHO', 'Trabalho formal/informal'),
        ('BENEFICIO_SOCIAL', 'Benefício social (BPC, Bolsa Família)'),
        ('PENSÃO', 'Pensão alimentícia'),
        ('APOSENTADORIA', 'Aposentadoria'),
        ('OUTROS', 'Outros'),
    ]
    
    ACESSO_SAUDE_CHOICES = [
        ('SUS', 'Sistema Único de Saúde (SUS)'),
        ('PLANODE_SAUDE', 'Plano de saúde privado'),
        ('PARTICULAR', 'Particular'),
        ('NAO_ACESSA', 'Não acessa serviços de saúde'),
    ]
    
    # Relacionamento com estudante e período de inscrição
    student = models.ForeignKey(
        'students.Student', 
        on_delete=models.CASCADE, 
        related_name='enrollments'
    )
    enrollment_period = models.ForeignKey(
        EnrollmentPeriod, 
        on_delete=models.CASCADE, 
        related_name='enrollments'
    )
    
    # Status da inscrição
    status = models.CharField(
        _('Status'), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='RASCUNHO'
    )
    
    # Informações de deslocamento (inline ou referência)
    displacement = models.OneToOneField(
        Displacement, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='enrollment'
    )
    
    # Endereço (referência)
    address = models.OneToOneField(
        'family.Address', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='enrollment'
    )
    
    # Informações socioeconômicas
    indice_vulnerabilidade = models.DecimalField(
        _('Índice de vulnerabilidade estudantil'), 
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    foi_beneficiado_ultima_edicao = models.BooleanField(
        _('Foi beneficiado na última edição do programa?'), 
        default=False
    )
    foi_beneficiado_beneficio_eventual = models.BooleanField(
        _('Foi beneficiado na última edição do benefício eventual?'), 
        default=False
    )
    
    # Auxílios específicos
    auxilio_digital = models.BooleanField(_('Solicita auxílio digital?'), default=False)
    recebe_bolsa_estudantil = models.BooleanField(
        _('Recebe algum tipo de bolsa estudantil?'), 
        default=False
    )
    descricao_bolsa = models.CharField(
        _('Descrição da bolsa'), 
        max_length=255, 
        null=True, 
        blank=True
    )
    
    # Benefícios sociais
    beneficiario_social = models.BooleanField(
        _('É beneficiário de programa social ou possui inscrição no CadÚnico?'), 
        default=False
    )
    cpf_familiar_beneficiario = models.CharField(
        _('CPF do familiar beneficiário do BPC/Bolsa Família'), 
        max_length=14, 
        null=True, 
        blank=True
    )
    valor_programa_social = models.DecimalField(
        _('Valor recebido através do programa social (R$)'), 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    comprovante_programa_social = models.FileField(
        _('Comprovante do programa social ou CADÚnico'), 
        upload_to='documents/social/', 
        null=True, 
        blank=True
    )
    
    # Chefia de família
    eh_chefe_familia = models.BooleanField(
        _('Você é chefe de família ou responsável pela própria subsistência?'), 
        default=False
    )
    grau_parentesco_chefe = models.CharField(
        _('Qual o grau de parentesco da pessoa que chefia a família?'), 
        max_length=100, 
        null=True, 
        blank=True
    )
    
    # Renda familiar
    renda_bruta_familiar = models.DecimalField(
        _('Renda bruta familiar (R$)'), 
        max_digits=12, 
        decimal_places=2, 
        default=0.00
    )
    renda_per_capita = models.DecimalField(
        _('Renda per capita (R$)'), 
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )
    faixa_renda_per_capita = models.CharField(
        _('Faixa de renda per capita'), 
        max_length=30, 
        choices=FAIXA_RENDA_CHOICES,
        null=True, 
        blank=True
    )
    renda_per_capita_extenso = models.CharField(
        _('Renda per capita (por extenso)'), 
        max_length=255, 
        null=True, 
        blank=True
    )
    origem_renda_principal = models.CharField(
        _('Qual a origem da renda principal de sua família?'), 
        max_length=30, 
        choices=ORIGEM_RENDA_CHOICES,
        null=True, 
        blank=True
    )
    
    # Acessos e serviços
    alimentacao_escolar = models.BooleanField(
        _('Utiliza alimentação no ambiente escolar?'), 
        default=False
    )
    xerox = models.BooleanField(_('Solicita auxílio para xerox?'), default=False)
    internet = models.BooleanField(_('Solicita auxílio para internet?'), default=False)
    acesso_saude = models.CharField(
        _('Como você acessa os serviços de saúde?'), 
        max_length=30, 
        choices=ACESSO_SAUDE_CHOICES,
        null=True, 
        blank=True
    )
    acesso_educacao_fundamental = models.TextField(
        _('Como você acessou à educação básica (Ensino Fundamental)?'), 
        null=True, 
        blank=True
    )
    acesso_educacao_medio = models.TextField(
        _('Como você acessa/acessou à educação básica (Ensino Médio)?'), 
        null=True, 
        blank=True
    )
    frequentou_proifpe = models.BooleanField(
        _('Frequentou o PROIFPE (curso pré-vestibular do IFPE)?'), 
        default=False
    )
    
    # Informações adicionais
    relato_vida = models.TextField(
        _('Relato de vida'), 
        help_text=_('Conte um pouco sobre sua história e situação')
    )
    condicoes_programa = models.TextField(
        _('Condições do programa'), 
        null=True, 
        blank=True
    )
    declaracao_veracidade = models.BooleanField(
        _('Declaro que todas as informações são verdadeiras'), 
        default=False
    )
    
    # Dados de conclusão
    data_conclusao = models.DateTimeField(_('Data de conclusão da inscrição'), null=True, blank=True)
    documentacao_correta = models.BooleanField(_('Documentação correta?'), default=False)
    
    # Classificação da inscrição pelo assistente social
    classificacao = models.CharField(
        _('Classificação'), 
        max_length=30, 
        choices=CLASSIFICACAO_CHOICES, 
        default='ANALISE',
        help_text=_('Classificação da situação da inscrição pelo assistente social')
    )
    comentario_assistente_social = models.TextField(
        _('Comentário do assistente social'), 
        null=True, 
        blank=True,
        help_text=_('Observações do assistente social sobre a classificação')
    )
    data_classificacao = models.DateTimeField(
        _('Data da classificação'), 
        null=True, 
        blank=True
    )
    assistente_social_responsavel = models.CharField(
        _('Assistente social responsável'), 
        max_length=255, 
        null=True, 
        blank=True
    )
    
    # Análise do pedagogo
    aluno_contemplado_bolsa = models.BooleanField(
        _('Aluno contemplado com bolsa?'), 
        default=False
    )
    comentario_pedagogo = models.TextField(_('Comentário do pedagogo'), null=True, blank=True)
    valor_bolsa_permanencia = models.DecimalField(
        _('Valor da bolsa permanência (R$)'), 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    data_analise = models.DateTimeField(_('Data da análise'), null=True, blank=True)
    pedagogo_responsavel = models.CharField(
        _('Pedagogo responsável'), 
        max_length=255, 
        null=True, 
        blank=True
    )
    
    # Bens
    bens_moveis = models.TextField(
        _('Bens Móveis'), 
        help_text=_('Liste os bens móveis da família'),
        null=True, 
        blank=True
    )
    bens_imoveis = models.TextField(
        _('Bens Imóveis'), 
        help_text=_('Liste os bens imóveis da família'),
        null=True, 
        blank=True
    )
    
    # Timestamps
    criado_em = models.DateTimeField(_('Criado em'), auto_now_add=True)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Inscrição')
        verbose_name_plural = _('Inscrições')
        ordering = ['-criado_em']
        unique_together = ['student', 'enrollment_period']
    
    def __str__(self):
        return f"{self.student.nome_completo} - {self.enrollment_period.titulo}"
    
    def calcular_renda_per_capita(self):
        """Calcula a renda per capita baseada nos membros familiares."""
        # Implementação será feita no serviço de inscrição
        pass
    
    def submeter(self):
        """Submete a inscrição para análise e cria registro na tabela Inscricoes."""
        from inscricoes.models import Inscricao, Edital
        
        self.status = 'SUBMETIDA'
        self.data_conclusao = timezone.now()
        # Inicializa a classificação como 'Em Análise' quando submetida
        self.classificacao = 'ANALISE'
        self.save()
        
        # Criar ou atualizar instância correspondente em Inscricoes
        # Primeiro, obter ou criar o Edital correspondente ao EnrollmentPeriod
        edital, created_edital = Edital.objects.get_or_create(
            pk=self.enrollment_period.pk,
            defaults={
                'titulo': self.enrollment_period.titulo,
                'descricao': self.enrollment_period.descricao or '',
                'numero': f"EDITAL-{self.enrollment_period.pk}",
                'periodo_inscricao_abertura': self.enrollment_period.data_inicio,
                'periodo_inscricao_fechamento': self.enrollment_period.data_fim,
                'status': 'ATIVO' if self.enrollment_period.status == 'ABERTO' else 'FECHADO',
                'ativo': self.enrollment_period.ativo,
            }
        )
        
        # Obter ou criar o Estudante correspondente ao Student
        from core.models import Estudante
        estudante, created_estudante = Estudante.objects.get_or_create(
            cpf=self.student.cpf,
            defaults={
                'nome_completo': self.student.nome_completo or '',
                'matricula': self.student.matricula or '',
                'email_institucional': self.student.email_institucional or '',
                'curso': self.student.curso or '',
                'campus': self.student.campus or '',
            }
        )
        
        # Criar ou atualizar a Inscrição correspondente
        inscricao, created = Inscricao.objects.get_or_create(
            edital=edital,
            estudante=estudante,
            defaults={
                'status': 'SUBMETIDA',
                'classificacao': 'ANALISE',
                'submetida_em': self.data_conclusao,
                'informacoes_estudante': {
                    'nome': self.student.nome_completo,
                    'cpf': self.student.cpf,
                    'matricula': self.student.matricula,
                    'data_nascimento': str(self.student.data_nascimento) if self.student.data_nascimento else '',
                    'raca': self.student.raca or '',
                    'sexo': self.student.sexo or '',
                },
                'informacoes_endereco': {
                    'cep': self.address.cep if self.address else '',
                    'bairro': self.address.bairro if self.address else '',
                    'cidade': self.address.cidade if self.address else '',
                    'estado': self.address.estado if self.address else '',
                    'rua': self.address.rua if self.address else '',
                    'numero': self.address.numero if self.address else '',
                    'complemento': self.address.complemento if self.address else '',
                } if self.address else {},
                'informacoes_deslocamento': {
                    'tipo_transporte': self.displacement.tipo_transporte if self.displacement else '',
                    'valor_mensal_transporte': str(self.displacement.valor_mensal_transporte) if self.displacement else '0',
                    'trajeto_percorrido': self.displacement.trajeto_percorrido if self.displacement else '',
                } if self.displacement else {},
                'informacoes_inscricao': {
                    'renda_bruta_familiar': str(self.renda_bruta_familiar),
                    'renda_per_capita': str(self.renda_per_capita),
                    'faixa_renda_per_capita': self.faixa_renda_per_capita or '',
                    'relato_vida': self.relato_vida or '',
                    'eh_chefe_familia': self.eh_chefe_familia,
                    'beneficiario_social': self.beneficiario_social,
                },
            }
        )
        
        # Se a inscrição já existia, atualizar os dados
        if not created:
            inscricao.status = 'SUBMETIDA'
            inscricao.classificacao = 'ANALISE'
            inscricao.submetida_em = self.data_conclusao
            inscricao.save()
    
    def classificar(self, classificacao, assistente_social=None, comentario=None):
        """
        Classifica a inscrição pelo assistente social.
        
        Args:
            classificacao: Código da classificação (ex: 'ELEGIVEL', 'NAO_ELEGIVEL')
            assistente_social: Nome ou usuário do assistente social responsável
            comentario: Observações sobre a classificação
        """
        from django.utils import timezone
        
        self.classificacao = classificacao
        self.data_classificacao = timezone.now()
        if assistente_social:
            self.assistente_social_responsavel = assistente_social
        if comentario:
            self.comentario_assistente_social = comentario
        self.save()
    
    def pode_editar(self):
        """Verifica se a inscrição ainda pode ser editada."""
        return self.status in ['RASCUNHO'] and self.enrollment_period.esta_aberto()
