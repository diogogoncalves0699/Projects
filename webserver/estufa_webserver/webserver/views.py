# webserver/views.py

import json

import pandas as pd
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.core.serializers.json import DjangoJSONEncoder
from django.http import (HttpResponse, HttpResponseNotAllowed,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .auth_backend import UtilizadorBackend
from .filters import LeituraFilter
from .forms import (LoginUtilizadorForm, RegistroUtilizadorForm,
                    SimulatedSystemForm, UserSystemAssignmentForm)
from .models import Leitura, SimulatedSystem, UserSystemAssignment, Utilizador

limites = {
        'temperatura': {'min': 10, 'max': 30},
        'humidade': {'min': 30, 'max': 70},
        'luz': {'min': 200, 'max': 800},
        'humidade_solo': {'min': 20, 'max': 70},
        'profundidade': {'min': 20, 'max': 80},
    }

def registro(request):
    print("View de Registro - Entrou na view de registro.")
    if request.method == 'POST':
        print("View de Registro - Método POST detectado.")
        form = RegistroUtilizadorForm(request.POST)
        if form.is_valid():
            form.save()
            print("View de Registro - Utilizador registrado com sucesso.")
            messages.success(request, 'Registrado com sucesso!')
            return redirect('login')
        else:
            print("View de Registro - Formulário de Registro inválido.")
    else:
        print("View de Registro - Método GET detectado.")
        form = RegistroUtilizadorForm()
    return render(request, 'signup.html', {'form': form})

def view_utilizadores(request):
    if not request.user.is_authenticated or not request.user.admin:
        return redirect('login')
    utilizadores = Utilizador.objects.all().values('id', 'nome', 'email', 'admin')
    return render(request, 'utilizadores.html', {'utilizadores': utilizadores})

def edit_admin(request, id):
    utilizador = get_object_or_404(Utilizador, id=id)
    if request.method == 'POST':
        utilizador.admin = not utilizador.admin
        utilizador.save()
        return redirect('utilizadores')
    return render(request, 'edit_admin.html', {'utilizador': utilizador})

def delete_utilizador(request, id):
    utilizador = get_object_or_404(Utilizador, id=id)
    if request.method == 'POST':
        utilizador.delete()
        return redirect('utilizadores')
    return render(request, 'delete_utilizador.html', {'utilizador': utilizador})

def custom_login(request, user, backend):
    request.session['_auth_user_id'] = user.pk
    request.session['_auth_user_backend'] = backend

def login_view(request):
    print("View de Login - Entrou na view de login.")
    if request.method == 'POST':
        print("View de Login - Método POST detectado.")
        form = LoginUtilizadorForm(request.POST)
        if form.is_valid():
            print("View de Login - Formulário de Login válido.")
            user = form.get_user()
            print(f"View de Login - Utilizador autenticado: {user}")
            custom_login(request, user, 'webserver.auth_backend.UtilizadorBackend')
            return redirect('home')
        else:
            print("View de Login - Formulário de Login inválido.")
    else:
        print("View de Login - Método GET detectado.")
        form = LoginUtilizadorForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def assign_system_to_user(request, utilizador_id):
    utilizador = Utilizador.objects.get(id=utilizador_id)
    if request.method == 'POST':
        form = UserSystemAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.utilizador = utilizador
            assignment.save()
            return redirect('users-with-systems')
    else:
        form = UserSystemAssignmentForm()
    return render(request, 'create_assignment.html', {'form': form, 'utilizador': utilizador})

def list_users_with_systems(request):
    # A consulta abaixo assume que você tem uma chave estrangeira de UserSystemAssignment para Utilizador
    utilizadores = Utilizador.objects.prefetch_related('usersystemassignment_set__sistema').all()
    return render(request, 'users_with_systems.html', {'utilizadores': utilizadores})

def home(request):
    return render(request, 'home.html')

@login_required
def sistemas(request):
    if request.user.admin:  # Verificando se o utilizador é admin
        sistemas = SimulatedSystem.objects.all()
    else:
        # Filtrando sistemas que estão explicitamente associados ao usuário através de UserSystemAssignment
        sistemas = SimulatedSystem.objects.filter(usersystemassignment__utilizador=request.user)

    avisos = {}
    for sistema in sistemas:
        ultima_leitura = Leitura.objects.filter(planta=sistema.nome_planta).order_by('-timestamp').first()
        sistema.ultima_leitura = ultima_leitura
        avisos[sistema.nome_planta] = []

        if ultima_leitura:
            for campo, limite in limites.items():
                valor = getattr(ultima_leitura, campo, None)
                if valor is not None and valor != 0:  # Adicionada condição para omitir valores zero
                    if valor < limite['min']:
                        avisos[sistema.nome_planta].append(f"{campo.capitalize()} muito baixa: {valor} < {limite['min']}")
                    elif valor > limite['max']:
                        avisos[sistema.nome_planta].append(f"{campo.capitalize()} muito alta: {valor} > {limite['max']}")

    return render(request, 'sistemas.html', {'sistemas': sistemas, 'avisos': avisos})



# Adicionar sistema
def adicionar_sistema(request):
    if request.method == 'POST':
        form = SimulatedSystemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sistemas')
    else:
        form = SimulatedSystemForm()
    return render(request, 'adicionar_sistema.html', {'form': form})

# Editar sistema
def editar_sistema(request, id):
    sistema = get_object_or_404(SimulatedSystem, id=id)
    if request.method == 'POST':
        form = SimulatedSystemForm(request.POST, instance=sistema)
        if form.is_valid():
            form.save()
            return redirect('sistemas')
    else:
        form = SimulatedSystemForm(instance=sistema)
    return render(request, 'editar_sistema.html', {'form': form})

# apagar sistema
def apagar_sistema(request, id):
    sistema = get_object_or_404(SimulatedSystem, id=id)
    if request.method == 'POST':
        sistema.delete()
        return redirect('sistemas')
    return render(request, 'confirmar_apagar.html', {'sistema': sistema})

def editar_temp_a(request, pk):
    sistema = get_object_or_404(SimulatedSystem, pk=pk)
    if request.method == 'POST':
        form = SimulatedSystemForm(request.POST, instance=sistema)
        if form.is_valid():
            form.save()
            return redirect('sistemas')
    else:
        form = SimulatedSystemForm(instance=sistema)

    return render(request, 'tempo_amostra.html', {'form': form})

def ver_dados(request, nome_planta):
    # Filtrar inicialmente pela planta especificada
    initial_queryset = Leitura.objects.filter(planta=nome_planta)
    
    leituras_filter = LeituraFilter(request.GET, queryset=Leitura.objects.filter(planta=nome_planta).order_by('-timestamp'))

    # Renderizar o template com os dados filtrados
    return render(request, 'dados.html', {'leituras_filter': leituras_filter})

def dados_graficos(request, nome_planta):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    leituras = Leitura.objects.filter(planta=nome_planta)

    if start_date:
        leituras = leituras.filter(timestamp__gte=start_date)
    if end_date:
        leituras = leituras.filter(timestamp__lte=end_date)

    data = {
        'dates': [leitura.timestamp.strftime('%Y-%m-%d %H:%M:%S') for leitura in leituras],
        'temperatura': [leitura.temperatura for leitura in leituras],
        'humidade': [leitura.humidade for leitura in leituras],
        'luz': [leitura.luz for leitura in leituras],
        'humidade_solo': [leitura.humidade_solo for leitura in leituras],
        'profundidade': [leitura.profundidade for leitura in leituras],
    }
    return render(request, 'graficos.html', {'data': json.dumps(data)})

@login_required
def unassign_system(request, assignment_id):
    if request.user.admin:  # Verifica se o usuário é admin
        assignment = get_object_or_404(UserSystemAssignment, id=assignment_id)
        assignment.delete()
        print(f"Requested ID for deletion: {assignment_id}")
        messages.success(request, "Sistema desassociado com sucesso.")
    else:
        messages.error(request, "Você não tem permissão para realizar esta ação.")
    return redirect('users-with-systems')

@login_required
def dados_view(request):
    # Cria uma instância do filtro com os dados GET da requisição e o queryset de todas as leituras
    leituras_filter = LeituraFilter(request.GET, queryset=Leitura.objects.all())

    # Passa o filtro para o template, em vez do queryset diretamente
    return render(request, 'dados.html', {'leituras_filter': leituras_filter})

@login_required
def delete_user(request, username):
    if request.user.is_superuser:
        user = User.objects.get(username=username)
        user.delete()


        # Redirecionar após deletar o usuário
    # Redirecionar se o usuário não for um superusuário
        
