# webserver/filters.py
import django_filters
from django import forms

from .models import Leitura, SimulatedSystem


class LeituraFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name="timestamp",
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = django_filters.DateFilter(
        field_name="timestamp",
        lookup_expr='lte',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    planta = django_filters.ChoiceFilter(
        label='Planta',
        field_name='planta',  # Este é o campo em Leitura
        choices=[],  # Inicialmente vazio
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Leitura
        fields = ['temperatura', 'humidade', 'luz', 'humidade_solo', 'profundidade', 'start_date', 'end_date', 'planta', 'Time']

    def __init__(self, *args, **kwargs):
        super(LeituraFilter, self).__init__(*args, **kwargs)
        self.filters['planta'].field.choices = [(planta.nome_planta, planta.nome_planta) for planta in SimulatedSystem.objects.all()]