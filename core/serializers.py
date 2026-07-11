"""
Serializers do app core - Serializadores para Estudante e Endereco.

Este módulo contém os serializadores que convertem modelos Django
em JSON e vice-versa para a API REST.
"""
from rest_framework import serializers
from .models import Estudante, Endereco


class EstudanteSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Estudante.
    
    Converte dados do estudante entre JSON e o modelo Django,
    incluindo validações e formatação de campos.
    """
    class Meta:
        model = Estudante
        fields = '__all__'
        read_only_fields = ['criado_em', 'atualizado_em']


class EnderecoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Endereco.
    
    Converte dados de endereço entre JSON e o modelo Django,
    incluindo o relacionamento com o estudante.
    """
    estudante_nome = serializers.CharField(source='estudante.nome_completo', read_only=True)
    
    class Meta:
        model = Endereco
        fields = '__all__'
        read_only_fields = ['criado_em', 'atualizado_em']
