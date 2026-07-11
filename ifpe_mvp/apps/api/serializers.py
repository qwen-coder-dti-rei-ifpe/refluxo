"""
Serializers do aplicativo API - Conversão de modelos para JSON
"""
from rest_framework import serializers
from students.models import Student
from family.models import Address, FamilyMember
from enrollments.models import EnrollmentPeriod, Enrollment, Displacement


class StudentSerializer(serializers.ModelSerializer):
    """Serializer para modelo Student."""
    
    class Meta:
        model = Student
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    """Serializer para modelo Address."""
    
    class Meta:
        model = Address
        fields = '__all__'


class FamilyMemberSerializer(serializers.ModelSerializer):
    """Serializer para modelo FamilyMember."""
    
    class Meta:
        model = FamilyMember
        fields = '__all__'


class DisplacementSerializer(serializers.ModelSerializer):
    """Serializer para modelo Displacement."""
    
    class Meta:
        model = Displacement
        fields = '__all__'


class EnrollmentPeriodSerializer(serializers.ModelSerializer):
    """Serializer para modelo EnrollmentPeriod."""
    
    esta_aberto = serializers.ReadOnlyField()
    
    class Meta:
        model = EnrollmentPeriod
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer para modelo Enrollment."""
    
    student_name = serializers.ReadOnlyField(source='student.nome_completo')
    period_title = serializers.ReadOnlyField(source='enrollment_period.titulo')
    pode_editar = serializers.ReadOnlyField()
    
    class Meta:
        model = Enrollment
        fields = '__all__'
        read_only_fields = ['student', 'enrollment_period', 'status', 'data_conclusao']


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de inscrição."""
    
    class Meta:
        model = Enrollment
        fields = ['student', 'enrollment_period']
