# webserver/models.py



from django.db import models


class MinhaModel(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()

class Leitura(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    temperatura = models.FloatField(blank=True, null=True)
    humidade = models.FloatField(blank=True, null=True)
    luz = models.FloatField(blank=True, null=True)
    humidade_solo = models.IntegerField(blank=True, null=True)
    profundidade = models.IntegerField(blank=True, null=True)
    planta = models.CharField(max_length=100)
    Time = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'leituras'
        ordering = ['-timestamp']


class SimulatedSystem(models.Model):
    sensor_dht = models.BooleanField(default=False, verbose_name="Sensor DHT (temperatura e humidade)?")
    sensor_bh1750 = models.BooleanField(default=False, verbose_name="Sensor BH1750 (luz)?")
    sensor_umidade_solo = models.BooleanField(default=False, verbose_name="Sensor de humidade do solo?")
    sensor_profundidade = models.BooleanField(default=False, verbose_name="Sensor de profundidade?")
    nome_planta = models.CharField(max_length=100, verbose_name="Nome da planta")
    temp_a = models.IntegerField(default=0, verbose_name="Tempo Amostragem")

    def __str__(self):
        # This defines what will be shown in the Django admin or any debug output for this model's instances
        details = [
            self.nome_planta,
            "DHT" if self.sensor_dht else "",
            "BH1750" if self.sensor_bh1750 else "",
            "Umidade do Solo" if self.sensor_umidade_solo else "",
            "Profundidade" if self.sensor_profundidade else ""
        ]
        return ", ".join(filter(None, details))  # Filters out empty strings

    class Meta:
        db_table = 'sistema_simulado'


class Utilizador(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    admin = models.BooleanField(default=False)

    class Meta:
        db_table = 'utilizadores'

    def __str__(self):
        return f"{self.nome} ({self.email})"
    
    @property
    def is_authenticated(self):
        """
        Simplesmente retorna True, necessário para compatibilidade com o backend de autenticação do Django.
        """
        return True
    
class UserSystemAssignment(models.Model):
    sistema = models.ForeignKey(SimulatedSystem, on_delete=models.CASCADE, verbose_name="Sistema")
    utilizador = models.ForeignKey(Utilizador, on_delete=models.CASCADE, verbose_name="Utilizador")

    class Meta:
        db_table = 'sistema_utilizador'

    def __str__(self):
        return f'{self.sistema.nome_planta} - {self.utilizador.username}'