"""
Forms do aplicativo Students - Formulários para cadastro e edição de estudantes
"""
from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    """
    Formulário principal para cadastro e edição de estudantes.
    Inclui todos os campos necessários para o programa de apoio acadêmico.
    """
    
    class Meta:
        model = Student
        fields = '__all__'
        exclude = ['user', 'criado_em', 'atualizado_em']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00', 'maxlength': '14'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'identidade': forms.TextInput(attrs={'class': 'form-control'}),
            'raca': forms.Select(attrs={'class': 'form-select'}),
            'cor': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'orientacao_sexual': forms.Select(attrs={'class': 'form-select'}),
            'genero': forms.TextInput(attrs={'class': 'form-control'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Matrícula'}),
            'campus': forms.TextInput(attrs={'class': 'form-control'}),
            'curso': forms.TextInput(attrs={'class': 'form-control'}),
            'turno': forms.Select(attrs={'class': 'form-select'}),
            'periodo': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantidade_disciplinas': forms.NumberInput(attrs={'class': 'form-control'}),
            'origem_escolar': forms.Select(attrs={'class': 'form-select'}),
            'eh_cotista': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'moradia_estudantil': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_institucional': forms.EmailInput(attrs={'class': 'form-control', 'type': 'email'}),
            'telefone_celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'tipo_conta': forms.Select(attrs={'class': 'form-select'}),
            'numero_agencia': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_conta': forms.TextInput(attrs={'class': 'form-control'}),
            'banco': forms.Select(attrs={'class': 'form-select'}),
            'banco_outro': forms.TextInput(attrs={'class': 'form-control'}),
            'identidade_cpf_anexo': forms.FileInput(attrs={'class': 'form-control'}),
            'identidade_frente': forms.FileInput(attrs={'class': 'form-control'}),
            'identidade_verso': forms.FileInput(attrs={'class': 'form-control'}),
        }


class StudentSearchForm(forms.Form):
    """
    Formulário para busca de estudante por matrícula ou CPF.
    Usado na página inicial para consulta e autopreenchimento.
    """
    
    TIPO_BUSCA_CHOICES = [
        ('MATRICULA', 'Matrícula'),
        ('CPF', 'CPF'),
    ]
    
    tipo_busca = forms.ChoiceField(
        label='Tipo de busca',
        choices=TIPO_BUSCA_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    valor_busca = forms.CharField(
        label='Valor',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a matrícula ou CPF'
        })
    )
