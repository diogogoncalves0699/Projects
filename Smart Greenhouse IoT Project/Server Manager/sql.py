import mysql.connector
import paho.mqtt.client as mqtt
from mysql.connector import Error

# Configurações do MQTT
mqtt_broker = "192.168.1.74"
mqtt_port = 1883
mqtt_topic = "emqx/esp32"

# Configurações do MySQL
mysql_host = 'localhost'
mysql_database = 'dados_sensores'
mysql_user = 'pitelecom'
mysql_password = 'estufa2324'

# Conectar ao MySQL
def connect_mysql():
    try:
        connection = mysql.connector.connect(host=mysql_host,
                                             database=mysql_database,
                                             user=mysql_user,
                                             password=mysql_password)
        if connection.is_connected():
            return connection
    except Error as e:
        print("Erro ao conectar ao MySQL:", e)
        return None

# Função para inserir dados
def insert_data(temperatura, humidade, luz, humidade_solo, profundidade, planta, time):
    try:
        connection = connect_mysql()
        if connection is not None:
            cursor = connection.cursor()
            sql_query = """INSERT INTO leituras (temperatura, humidade, luz, humidade_solo, profundidade, planta, Time) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s);"""
            cursor.execute(sql_query, (temperatura, humidade, luz, humidade_solo, profundidade, planta, time))
            connection.commit()
            cursor.close()
            connection.close()
            print("Dados inseridos com sucesso!")
    except Error as e:
        print("Erro ao inserir dados no MySQL:", e)

def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print(f"Mensagem recebida: {msg}")

    try:
        parts = msg.split(',')
        temperatura = float(parts[0].split(':')[1].strip()[:-1])
        humidade = float(parts[1].split(':')[1].strip()[:-1])
        luz = float(parts[2].split(':')[1].strip()[:-3])
        humidade_solo = float(parts[3].split(':')[1].strip()[:-1])
        profundidade = float(parts[4].split(':')[1].strip()[:-1])
        planta = parts[5].split(':')[1].strip()
        time = parts[6].split(':')[1].strip()
        insert_data(temperatura, humidade, luz, humidade_solo, profundidade, planta, time)
    except (ValueError, IndexError) as e:
        print(f"Erro ao parsear a mensagem: {e}")

# Configuração do cliente MQTT
client = mqtt.Client()
client.connect(mqtt_broker, mqtt_port)
client.subscribe(mqtt_topic)
client.on_message = on_message

# Iniciar loop
client.loop_forever()


