from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import check_password

from .models import SimulatedSystem, UserSystemAssignment, Utilizador


class SimulatedSystemForm(forms.ModelForm):
    class Meta:
        model = SimulatedSystem
        fields = '__all__'

class LoginUtilizadorForm(forms.Form):
    nome = forms.CharField(label="Nome")
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        nome = self.cleaned_data.get('nome')
        password = self.cleaned_data.get('password')
        print(f"Formulário de Login - Nome: {nome}, Senha: {password}")

        try:
            user = Utilizador.objects.get(nome=nome)
            print(f"Formulário de Login - Utilizador encontrado: {user}")
        except Utilizador.DoesNotExist:
            print("Formulário de Login - Utilizador não encontrado.")
            raise forms.ValidationError("Utilizador não encontrado.")

        # Verificar senha diretamente
        if user.password != password:
            print("Formulário de Login - Senha incorreta.")
            raise forms.ValidationError("Senha incorreta.")
        else:
            print("Formulário de Login - Senha correta.")

        self.user = user
        return self.cleaned_data

    def get_user(self):
        return self.user

class RegistroUtilizadorForm(forms.ModelForm):
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirme a Senha', widget=forms.PasswordInput)

    class Meta:
        model = Utilizador
        fields = ['nome', 'email']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = self.cleaned_data["password1"]
        if commit:
            user.save()
        return user

class UserSystemAssignmentForm(forms.ModelForm):
    class Meta:
        model = UserSystemAssignment
        fields = ['sistema', 'utilizador']