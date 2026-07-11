"""
Serializers do app integrations - Serializadores para modelos mock.

Este módulo contém os serializadores para os modelos de integração
com APIs externas (QAcadêmico e ConectaGov).
"""
from rest_framework import serializers
from .models import QAcademicoMock, ConectaGovMock


class QAcademicoMockSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo QAcademicoMock.
    
    Converte dados mock do QAcadêmico entre JSON e o modelo Django.
    """
    class Meta:
        model = QAcademicoMock
        fields = '__all__'


class ConectaGovMockSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo ConectaGovMock.
    
    Converte dados mock do ConectaGov entre JSON e o modelo Django.
    """
    class Meta:
        model = ConectaGovMock
        fields = '__all__'
