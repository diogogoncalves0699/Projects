# webserver/urls.py

from django.urls import path

from . import views
from .views import (adicionar_sistema, apagar_sistema, assign_system_to_user,
                    dados_graficos, editar_sistema, editar_temp_a,
                    list_users_with_systems, login_view, sistemas,
                    unassign_system, ver_dados)

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('signup/', views.registro, name='signup'),
    path('delete_user/<str:username>/', views.delete_user, name='delete_user'),
    path('dados/', views.dados_view, name='dados'),
    path('sistemas/', views.sistemas, name='sistemas'),
    path('adicionar/', adicionar_sistema, name='adicionar_sistema'),
    path('editar/<int:id>/', editar_sistema, name='editar_sistema'),
    path('apagar/<int:id>/', apagar_sistema, name='apagar_sistema'),
    path('sistema/editar/<int:pk>/', editar_temp_a, name='editar_temp_a'),
    path('dados/<str:nome_planta>/', ver_dados, name='ver_dados'),
    path('graficos/<str:nome_planta>/', views.dados_graficos, name='dados-graficos'),
    path('utilizadores/', views.view_utilizadores, name='utilizadores'),
    path('utilizadores/edit-admin/<int:id>/', views.edit_admin, name='edit_admin'),
    path('utilizadores/delete/<int:id>/', views.delete_utilizador, name='delete_utilizador'),
    path('assign-system/<int:utilizador_id>/', assign_system_to_user, name='assign_system'),
    path('users-with-systems/', list_users_with_systems, name='users-with-systems'),
    path('unassign-system/<int:assignment_id>/', unassign_system, name='unassign_system'),
]
