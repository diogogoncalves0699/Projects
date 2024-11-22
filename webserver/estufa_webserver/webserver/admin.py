# webserver/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import (Leitura, MinhaModel, SimulatedSystem,
                     UserSystemAssignment, Utilizador)


class UtilizadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'email', 'admin')
    search_fields = ('nome', 'email')
    list_filter = ('admin',)

admin.site.register(Utilizador, UtilizadorAdmin)
admin.site.register(SimulatedSystem)
admin.site.register(UserSystemAssignment)
class LeituraAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'temperatura', 'umidade', 'luz', 'umidade_solo', 'profundidade')
    list_filter = ('timestamp',)