from django.contrib import admin
from .models import Edital, Inscricao, Analise, MembroFamiliar


@admin.register(Edital)
class EditalAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar editais do programa.
    
    Permite ao controlador:
    - Visualizar todos os editais
    - Alterar períodos de inscrição e avaliação
    - Ativar, suspender ou cancelar editais
    """
    list_display = ['numero', 'titulo', 'status', 'periodo_inscricao_abertura', 
                    'periodo_inscricao_fechamento', 'periodo_avaliacao_abertura', 
                    'periodo_avaliacao_fechamento', 'ativo', 'criado_em']
    list_filter = ['status', 'ativo', 'criado_em']
    search_fields = ['numero', 'titulo', 'descricao']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero', 'titulo', 'descricao')
        }),
        ('Período de Inscrições', {
            'fields': ('periodo_inscricao_abertura', 'periodo_inscricao_fechamento'),
            'description': 'Defina o período para inscrições dos estudantes'
        }),
        ('Período de Avaliação', {
            'fields': ('periodo_avaliacao_abertura', 'periodo_avaliacao_fechamento'),
            'description': 'Defina o período para avaliação dos pedagogos'
        }),
        ('Status', {
            'fields': ('status', 'ativo'),
            'description': 'Controle o status do edital (Ativo, Suspenso, Cancelado, Finalizado)'
        }),
    )
    
    actions = ['ativar_editais', 'suspender_editais', 'cancelar_editais']
    
    def ativar_editais(self, request, queryset):
        queryset.update(status='ATIVO', ativo=True)
        self.message_user(request, 'Editais ativados com sucesso.')
    ativar_editais.short_description = "Ativar editais selecionados"
    
    def suspender_editais(self, request, queryset):
        queryset.update(status='SUSPENSO')
        self.message_user(request, 'Editais suspensos com sucesso.')
    suspender_editais.short_description = "Suspender editais selecionados"
    
    def cancelar_editais(self, request, queryset):
        queryset.update(status='CANCELADO', ativo=False)
        self.message_user(request, 'Editais cancelados com sucesso.')
    cancelar_editais.short_description = "Cancelar editais selecionados"


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar inscrições dos estudantes.
    
    Permite ao pedagogo:
    - Visualizar todas as inscrições por edital
    - Classificar inscrições (Análise, Com Pendência, Regularizado, etc.)
    - Acompanhar status das submissões
    """
    list_display = ['estudante', 'edital', 'status', 'classificacao', 'submetida_em', 'criado_em']
    list_filter = ['edital', 'status', 'classificacao', 'criado_em']
    search_fields = ['estudante__nome_completo', 'estudante__cpf', 'estudante__matricula', 'edital__numero']
    
    fieldsets = (
        ('Informações da Inscrição', {
            'fields': ('edital', 'estudante', 'status', 'classificacao')
        }),
        ('Dados do Estudante', {
            'fields': ('informacoes_estudante',),
            'classes': ('collapse',)
        }),
        ('Dados do Endereço', {
            'fields': ('informacoes_endereco',),
            'classes': ('collapse',)
        }),
        ('Dados Familiares', {
            'fields': ('informacoes_familiares',),
            'classes': ('collapse',)
        }),
        ('Dados de Deslocamento', {
            'fields': ('informacoes_deslocamento',),
            'classes': ('collapse',)
        }),
        ('Dados da Inscrição', {
            'fields': ('informacoes_inscricao', 'documentos'),
            'classes': ('collapse',)
        }),
    )
    
    list_editable = ['classificacao']
    actions = ['marcar_analise', 'marcar_com_pendencia', 'marcar_regularizado', 
               'marcar_nao_regularizado', 'marcar_elegivel', 'marcar_nao_elegivel',
               'marcar_contemplado', 'marcar_nao_contemplado']
    
    def marcar_analise(self, request, queryset):
        queryset.update(classificacao='ANALISE')
        self.message_user(request, 'Inscrições marcadas como Em Análise.')
    marcar_analise.short_description = "Marcar como Em Análise"
    
    def marcar_com_pendencia(self, request, queryset):
        queryset.update(classificacao='COM_PENDENCIA')
        self.message_user(request, 'Inscrições marcadas como Com Pendência.')
    marcar_com_pendencia.short_description = "Marcar como Com Pendência"
    
    def marcar_regularizado(self, request, queryset):
        queryset.update(classificacao='REGULARIZADO')
        self.message_user(request, 'Inscrições marcadas como Regularizado.')
    marcar_regularizado.short_description = "Marcar como Regularizado"
    
    def marcar_nao_regularizado(self, request, queryset):
        queryset.update(classificacao='NAO_REGULARIZADO')
        self.message_user(request, 'Inscrições marcadas como Não Regularizado.')
    marcar_nao_regularizado.short_description = "Marcar como Não Regularizado"
    
    def marcar_elegivel(self, request, queryset):
        queryset.update(classificacao='ELEGIVEL')
        self.message_user(request, 'Inscrições marcadas como Elegível.')
    marcar_elegivel.short_description = "Marcar como Elegível"
    
    def marcar_nao_elegivel(self, request, queryset):
        queryset.update(classificacao='NAO_ELEGIVEL')
        self.message_user(request, 'Inscrições marcadas como Não Elegível.')
    marcar_nao_elegivel.short_description = "Marcar como Não Elegível"
    
    def marcar_contemplado(self, request, queryset):
        queryset.update(classificacao='CONTEMPLADO')
        self.message_user(request, 'Inscrições marcadas como Contemplado.')
    marcar_contemplado.short_description = "Marcar como Contemplado"
    
    def marcar_nao_contemplado(self, request, queryset):
        queryset.update(classificacao='NAO_CONTEMPLADO')
        self.message_user(request, 'Inscrições marcadas como Não Contemplado.')
    marcar_nao_contemplado.short_description = "Marcar como Não Contemplado"


@admin.register(Analise)
class AnaliseAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar análises das inscrições.
    """
    list_display = ['inscricao', 'pedagogo', 'data_analise', 'elegivel', 'deferida']
    list_filter = ['elegivel', 'deferida', 'data_analise']
    search_fields = ['inscricao__estudante__nome_completo', 'pedagogo', 'inscricao__edital__numero']
    
    fieldsets = (
        ('Informações da Análise', {
            'fields': ('inscricao', 'pedagogo', 'data_analise')
        }),
        ('Avaliação', {
            'fields': ('elegivel', 'indice_vulnerabilidade')
        }),
        ('Decisão', {
            'fields': ('deferida', 'valor_bolsa', 'comentario')
        }),
        ('Critérios', {
            'fields': ('criterios_avaliacao',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MembroFamiliar)
class MembroFamiliarAdmin(admin.ModelAdmin):
    """
    Admin para gerenciar membros familiares.
    """
    list_display = ['nome', 'parentesco', 'inscricao', 'rendimento_mensal']
    list_filter = ['parentesco', 'possui_agravo_saude', 'possui_necessidade_especifica']
    search_fields = ['nome', 'cpf', 'inscricao__estudante__nome_completo']