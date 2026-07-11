from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from .models import Estudante, Endereco

# Desregistrar modelos padrão para limpar o admin
admin.site.unregister(Group)

@admin.register(Estudante)
class EstudanteAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'matricula', 'curso', 'periodo', 'criado_em')
    search_fields = ('nome_completo', 'cpf', 'matricula', 'email_institucional')
    list_filter = ('campus', 'curso', 'turno', 'eh_cotista', 'moradia_estudantil')
    readonly_fields = ('criado_em', 'atualizado_em')
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome_completo', 'cpf', 'idade', 'identidade', 'raca', 'cor', 'sexo', 'orientacao_sexual', 'genero')
        }),
        ('Dados Acadêmicos', {
            'fields': ('matricula', 'campus', 'curso', 'turno', 'periodo', 'quantidade_disciplinas', 'origem_escolar', 'eh_cotista', 'moradia_estudantil')
        }),
        ('Contato', {
            'fields': ('email_institucional',)
        }),
        ('Dados Bancários', {
            'fields': ('tipo_conta', 'numero_agencia', 'numero_conta', 'banco'),
            'classes': ('collapse',)
        }),
        ('Documentos', {
            'fields': ('identidade_cpf_anexo', 'identidade_frente', 'identidade_verso'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('estudante', 'cidade', 'estado', 'cep')
    search_fields = ('estudante__nome_completo', 'cidade', 'cep')
    list_filter = ('estado', 'regiao_moradia')
    readonly_fields = ('criado_em', 'atualizado_em')
    
    fieldsets = (
        ('Localização', {
            'fields': ('estudante', 'cep', 'bairro', 'cidade', 'estado', 'ponto_referencia')
        }),
        ('Informações de Visita', {
            'fields': ('horario_visita', 'telefone_celular', 'procurar_por_pessoa', 'com_que_mora')
        }),
        ('Condições de Moradia', {
            'fields': ('condicoes_moradia_familiar', 'regiao_moradia', 'abastecimento_agua', 'material_construcao', 'saneamento'),
            'classes': ('collapse',)
        }),
        ('Contato de Referência', {
            'fields': ('contato_referencia_nome', 'contato_referencia_telefone'),
            'classes': ('collapse',)
        }),
        ('Outras Informações', {
            'fields': ('mudou_endereco_para_estudar',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


# Personalização do Admin Site
admin.site.site_header = "PAMA - Administração"
admin.site.site_title = "Admin PAMA"
admin.site.index_title = "Painel Administrativo"

# Customização da página inicial do admin
class CustomAdminSite(admin.AdminSite):
    site_header = "PAMA - Programa de Apoio e Manutenção Acadêmica"
    site_title = "Admin PAMA"
    index_title = "Painel de Controle"
    
    def get_app_list(self, request):
        """Retorna lista de aplicações filtrada por grupo de usuário"""
        app_list = super().get_app_list(request)
        
        # Se for superuser, mostra tudo
        if request.user.is_superuser:
            return app_list
        
        # Filtra baseado nos grupos do usuário
        if hasattr(request.user, 'groups'):
            group_names = [group.name for group in request.user.groups.all()]
            
            # Pedagogo: vê apenas inscrições para avaliação
            if 'Pedagogo' in group_names:
                app_list = [app for app in app_list if app['name'] == 'Core']
            
            # Controlador: vê apenas editais e períodos
            elif 'Controlador' in group_names:
                app_list = [app for app in app_list if app['name'] == 'Core']
        
        return app_list

# Substituir o admin site padrão pelo customizado
admin.site.__class__ = CustomAdminSite
