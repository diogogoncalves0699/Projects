# webserver/auth_backend.py

from django.contrib.auth.backends import BaseBackend

from .models import Utilizador


class UtilizadorBackend(BaseBackend):
    def authenticate(self, request, nome=None, password=None):
        print(f"Backend de Autenticação - Tentando autenticar com nome: {nome}")
        try:
            user = Utilizador.objects.get(nome=nome)
            print(f"Backend de Autenticação - Utilizador encontrado: {user}")
        except Utilizador.DoesNotExist:
            print("Backend de Autenticação - Utilizador não encontrado.")
            return None

        if user.password == password:
            print("Backend de Autenticação - Senha correta.")
            return user
        else:
            print("Backend de Autenticação - Senha incorreta.")
            return None

    def get_user(self, user_id):
        try:
            user = Utilizador.objects.get(pk=user_id)
            print(f"Backend de Autenticação - Encontrou o utilizador com ID: {user_id}")
            return user
        except Utilizador.DoesNotExist:
            print(f"Backend de Autenticação - Não encontrou o utilizador com ID: {user_id}")
            return None







