import csv
import random
import time
from datetime import datetime

import mysql.connector
import paho.mqtt.client as mqtt

# Configurações do MQTT
mqtt_broker = "192.168.1.74"
mqtt_port = 1883
mqtt_topic = "emqx/esp32"

valores_iniciais = {}

def simular_dados_sensores(sensores):
    global valores_iniciais
    dados = {}
    max_variacao_percentual = 0.05  # Variação máxima de 5%

    for sensor, ativo in sensores.items():
        if ativo:
            if sensor not in valores_iniciais:
                # Gerar valor inicial se ainda não existir
                if sensor == "DHT":
                    valores_iniciais[sensor] = {"temperatura": round(random.uniform(20, 30), 2),
                                                "humidade": round(random.uniform(40, 60), 2)}
                elif sensor == "BH1750":
                    valores_iniciais[sensor] = {"luz": round(random.uniform(100, 1000), 2)}
                elif sensor == "Humidade do Solo":
                    valores_iniciais[sensor] = {"humidade_solo": random.randint(30, 70)}
                elif sensor == "Profundidade":
                    valores_iniciais[sensor] = {"profundidade": random.randint(60, 100)}
            
            # Aplicar variação aos valores iniciais
            for key, value in valores_iniciais[sensor].items():
                variacao = random.uniform(-value * max_variacao_percentual, value * max_variacao_percentual)
                dados[key] = round(value + variacao, 2)
        else:
            # Se o sensor não estiver ativo, definir como 0 ou manter como None
            if sensor == "DHT":
                dados["temperatura"] = 0
                dados["humidade"] = 0
            elif sensor == "BH1750":
                dados["luz"] = 0
            elif sensor == "Humidade do Solo":
                dados["humidade_solo"] = 0
            elif sensor == "Profundidade":
                dados["profundidade"] = 0

    return dados

def definir_nome_planta():
    return input("Digite o nome da planta para o sistema simulado: ")

def conectar_banco():
    # Configurações de conexão ao banco de dados MySQL
    conexao = mysql.connector.connect(
        host='localhost',
        user='pitelecom',
        password='estufa2324',
        database='dados_sensores'
    )
    return conexao

def buscar_dados_sistema(conexao):
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM sistema_simulado")
    sistemas = cursor.fetchall()
    cursor.close()
    return sistemas

def selecionar_sistema(sistemas, id_sistema):
    for sistema in sistemas:
        if sistema[0] == id_sistema:  # Supondo que o ID do sistema seja o primeiro campo
            return sistema
    return None

def exibir_e_selecionar_sistema():
    conexao = conectar_banco()
    sistemas = buscar_dados_sistema(conexao)
    conexao.close()
    
    if sistemas:
        print("Sistemas Simulados:")
        for sistema in sistemas:
            print(f"ID: {sistema[0]}, Nome: {sistema[5]}, Temp. Amostragem: {sistema[6]} ")  # Adapte conforme a estrutura da sua tabela
        id_sistema = int(input("Digite o ID do sistema que deseja usar: "))
        sistema_selecionado = selecionar_sistema(sistemas, id_sistema)
        if sistema_selecionado:
            return sistema_selecionado
    else:
        print("Nenhum sistema simulado encontrado.")
    return None

def publicar_mqtt(mensagem):
    client = mqtt.Client()
    client.connect(mqtt_broker, mqtt_port, 60)
    client.publish(mqtt_topic, mensagem)
    client.disconnect()
    print(f"Mensagem publicada no MQTT: {mensagem}")

def usar_sistema_simulado(sistema_selecionado):
    sensores = {
        "DHT": sistema_selecionado[1],
        "BH1750": sistema_selecionado[2],
        "Humidade do Solo": sistema_selecionado[3],
        "Profundidade": sistema_selecionado[4]
    }
    nome_planta = sistema_selecionado[5]
    intervalo_amostragem = sistema_selecionado[6]  # Usando temp_a como intervalo de amostragem

    while True:
        dados = simular_dados_sensores(sensores)
        mensagem = criar_mensagem_mqtt(dados, nome_planta, intervalo_amostragem)
        publicar_mqtt(mensagem)
        time.sleep(intervalo_amostragem)

def ajustar_valores(dados):
    max_variacao_percentual = 0.05  # 5%
    dados_ajustados = dados.copy()  # Copiar os dados para manter os originais intactos

    campos_numericos = ['temperatura', 'humidade', 'luz', 'humidade_solo', 'profundidade']

    for campo in campos_numericos:
        valor = dados.get(campo, 'NULL')
        if valor != 'NULL':  # Ajusta apenas se o valor não for 'NULL'
            valor_base = float(valor)
            variacao = random.uniform(-max_variacao_percentual, max_variacao_percentual)
            novo_valor = valor_base + (valor_base * variacao)
            dados_ajustados[campo] = round(novo_valor, 2)

    return dados_ajustados

def criar_mensagem_mqtt(dados, planta, intervalo):
    # Ajustar os valores antes de criar a mensagem
    dados_ajustados = ajustar_valores(dados)
    planta = dados_ajustados.get('planta', planta)
    

    mensagem = f"Temperatura: {dados_ajustados.get('temperatura', 'NULL')} C, " \
               f"Humidade: {dados_ajustados.get('humidade', 'NULL')} %, " \
               f"Luz: {dados_ajustados.get('luz', 'NULL')} Lux, " \
               f"Humidade do Solo: {dados_ajustados.get('humidade_solo', 'NULL')} %, " \
               f"Profundidade: {dados_ajustados.get('profundidade', 'NULL')} %, " \
               f"Planta: {planta}, " \
               f"Time: {intervalo} s"

    return mensagem

def main():
    sistema_atual = None
    while True:
        print("\nMenu Principal")
        print("1 - Selecionar Sistema Simulado")
        print("2 - Usar Sistema Simulado")
        print("3 - Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            sistema_atual = exibir_e_selecionar_sistema()
        elif escolha == '2':
            if sistema_atual:
                usar_sistema_simulado(sistema_atual)
            else:
                print("Selecione um sistema primeiro.")
        elif escolha == '3':
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    main()

