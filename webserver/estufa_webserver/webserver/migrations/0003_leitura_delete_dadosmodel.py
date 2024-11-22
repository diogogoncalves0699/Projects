# Generated by Django 5.0.3 on 2024-03-30 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webserver', '0002_dadosmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Leitura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('temperatura', models.FloatField()),
                ('umidade', models.FloatField()),
                ('luz', models.FloatField()),
                ('umidade_solo', models.IntegerField()),
                ('profundidade', models.IntegerField()),
            ],
            options={
                'db_table': 'leituras',
            },
        ),
        migrations.DeleteModel(
            name='DadosModel',
        ),
    ]