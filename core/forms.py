"""
Forms personalizados para autenticação e jornada do estudante.

Este módulo contém formulários customizados para login com autopreenchimento
e formulário de jornada do estudante.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    """
    Formulário de login personalizado com campos estilizados.
    """
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu usuário',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha',
        })
    )


class JornadaForm(forms.Form):
    """
    Formulário para o fluxo de jornada do estudante.
    Permite ao estudante preencher seus dados em etapas.
    """
    
    # Etapa 1: Dados Pessoais
    nome_completo = forms.CharField(
        max_length=255, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'})
    )
    cpf = forms.CharField(
        max_length=14, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'})
    )
    idade = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    raca = forms.ChoiceField(
        choices=[
            ('', 'Selecione...'),
            ('BRANCA', 'Branca'),
            ('PRETA', 'Preta'),
            ('PARDA', 'Parda'),
            ('AMARELA', 'Amarela'),
            ('INDIGENA', 'Indígena'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sexo = forms.ChoiceField(
        choices=[
            ('', 'Selecione...'),
            ('M', 'Masculino'),
            ('F', 'Feminino'),
            ('O', 'Outro'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Etapa 2: Dados Acadêmicos
    matricula = forms.CharField(
        max_length=50, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número da matrícula'})
    )
    campus = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Campus'})
    )
    curso = forms.CharField(
        max_length=200, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Curso'})
    )
    turno = forms.ChoiceField(
        choices=[
            ('', 'Selecione...'),
            ('MATUTINO', 'Matutino'),
            ('VESPERTINO', 'Vespertino'),
            ('NOTURNO', 'Noturno'),
            ('INTEGRAL', 'Integral'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    periodo = forms.CharField(
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Período (ex: 1º, 2º)'})
    )
    eh_cotista = forms.BooleanField(required=False)
    moradia_estudantil = forms.BooleanField(required=False)
    
    # Etapa 3: Endereço
    cep = forms.CharField(
        max_length=9, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'})
    )
    bairro = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cidade = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    estado = forms.CharField(
        max_length=2, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'})
    )
    
    # Etapa 4: Dados Bancários (opcional)
    tipo_conta = forms.ChoiceField(
        choices=[
            ('', 'Selecione...'),
            ('CORRENTE', 'Corrente'),
            ('POUPANCA', 'Poupança'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    numero_agencia = forms.CharField(
        max_length=10, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numero_conta = forms.CharField(
        max_length=20, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    banco = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Etapa 5: Confirmação
    termo_ciencia = forms.BooleanField(
        required=True, 
        label="Declaro que todas as informações prestadas são verdadeiras",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
