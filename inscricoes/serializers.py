"""
Serializers do app inscricoes - Serializadores para editais, inscrições e análises.

Este módulo contém os serializadores para os modelos de gestão
do programa de apoio e manutenção acadêmica.
"""
from rest_framework import serializers
from .models import Edital, Inscricao, Analise


class EditalSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Edital.
    
    Inclui campo calculado para verificar se edital está aberto.
    """
    esta_aberto = serializers.SerializerMethodField()
    
    class Meta:
        model = Edital
        fields = '__all__'
        read_only_fields = ['criado_em', 'atualizado_em']
    
    def get_esta_aberto(self, obj):
        return obj.esta_aberto()


class InscricaoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Inscricao.
    
    Inclui dados do estudante e edital relacionados.
    """
    estudante_nome = serializers.CharField(source='estudante.nome_completo', read_only=True)
    estudante_matricula = serializers.CharField(source='estudante.matricula', read_only=True)
    edital_numero = serializers.CharField(source='edital.numero', read_only=True)
    pode_editar = serializers.SerializerMethodField()
    
    class Meta:
        model = Inscricao
        fields = '__all__'
        read_only_fields = ['submetida_em', 'criado_em', 'atualizado_em']
    
    def get_pode_editar(self, obj):
        return obj.pode_editar()


class AnaliseSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Analise.
    
    Inclui dados da inscrição analisada.
    """
    inscricao_estudante = serializers.CharField(source='inscricao.estudante.nome_completo', read_only=True)
    inscricao_edital = serializers.CharField(source='inscricao.edital.numero', read_only=True)
    
    class Meta:
        model = Analise
        fields = '__all__'
        read_only_fields = ['data_analise']


class DashboardEstudanteSerializer(serializers.Serializer):
    """
    Serializer para dados do dashboard do estudante.
    
    Agrega informações de múltiplos modelos para exibição no dashboard.
    """
    estudante = serializers.DictField()
    edital_aberto = serializers.DictField(allow_null=True)
    ja_inscrito = serializers.BooleanField()
    inscricao_atual = serializers.DictField(allow_null=True)
    historico_inscricoes = serializers.ListField(child=serializers.DictField())
    eixos_preenchidos = serializers.DictField()
