#include <BH1750.h>
#include <Wire.h>
#include <DHT.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Time.h>

#define WIFI_NETWORK "MEO-842E70"
#define WIFI_PASSWORD "fd5bbe8803"
#define WIFI_TIMEOUT_MS 20000

#define LED D3         
#define LED2 D4
const int PinoAnalogico = A0;
const int PinoDigital = D2;
const int readPin = A2; 
const int rele = D9;

const char *mqtt_broker = "192.168.1.74";
const char *mqtt_topic = "emqx/esp32";
const char *mqtt_username = "emqx";
const char *mqtt_password = "public";
const int mqtt_port = 1883;

DHT dht(PinoDigital, DHT22);
BH1750 lightMeter(0x23);

float temp, humidity, lux;
int valorAnalogico;
int moisture;
int value;                    
int moisture2;               

WiFiClient espClient;
PubSubClient mqtt_client(espClient);

unsigned long lastSensorReadTime = 0;
const unsigned long sensorReadInterval = 2000;
volatile bool sendToMQTTFlag = false;
unsigned long lastMQTTSendTime = 0;
const unsigned long mqttSendInterval = 16000;

void ConnectToWifi() {
  Serial.print("Connecting to WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_NETWORK, WIFI_PASSWORD);

  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < WIFI_TIMEOUT_MS) {
    Serial.print(".");
    delay(100);
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println(" Failed!");
    delay(5000);
    ESP.restart(); // Reiniciar se a conexão falhar
  } else {
    Serial.print(" Connected: ");
    Serial.println(WiFi.localIP());
  }
}

void connectToMQTT() {
  while (!mqtt_client.connected()) {
    String client_id = "esp32-client-" + String(WiFi.macAddress());
    if (mqtt_client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("Connected to MQTT broker");
      mqtt_client.subscribe(mqtt_topic);
    } else {
      Serial.print("MQTT connect failed, rc=");
      Serial.println(mqtt_client.state());
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(9600);
  Wire.begin();
  ConnectToWifi();
  mqtt_client.setServer(mqtt_broker, mqtt_port);
  mqtt_client.setCallback(mqttCallback);
  connectToMQTT();
  // Inicializar e obter o horário
  configTime(0, 0, "time.google.com");
  delay(1500); // Espera um pouco para obter a hora do servidor NTP
  if (!verifyLocalTime()) {
    Serial.println("Failed to verify local time.");
    delay(2000);
    verifyLocalTime();
    while (true) {} // Fica em um loop infinito se a hora não for verificada
  }
  dht.begin();
  pinMode(PinoAnalogico, INPUT);
  pinMode(LED, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(rele, OUTPUT);
  lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);

  // Verifica se os sensores estão ligados
  Serial.println("Checking if sensors are connected...");
  delay(2000);
  if (!dht.readTemperature() || !dht.readHumidity()) {
    Serial.println("DHT sensor not connected!");
  } else {
    Serial.println("DHT sensor connected!");
  }
  delay(2000);
  if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println(F("BH1750 sensor connected!"));
  } else {
    Serial.println(F("BH1750 sensor not connected!"));
  }
  delay(1000);
  Serial.println();
}

void loop() {
  if (!mqtt_client.connected()) {
    connectToMQTT();
  }
  mqtt_client.loop();

  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorReadTime > sensorReadInterval) {
    readSensorValues();
    printValues(); // Imprime os valores dos sensores e a data/hora
    lastSensorReadTime = currentMillis;
  }

  if (currentMillis - lastMQTTSendTime > mqttSendInterval) {
    sendSensorDataToMQTT("real", "16 s");
    lastMQTTSendTime = currentMillis;
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message received on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void readSensorValues() {
  temp = dht.readTemperature();
  if (isnan(temp)) {
    Serial.println("Failed to read temperature!");
  }

  humidity = dht.readHumidity();
  if (isnan(humidity)) {
    Serial.println("Failed to read humidity!");
  }

  valorAnalogico = analogRead(PinoAnalogico);
  moisture = map(valorAnalogico, 0, 4095, 0, 100); // Map the analog value to a moisture percentage

  value = analogRead(readPin);
  moisture2 = map(value, 0, 4095, 0, 100); // Map the analog value to a moisture percentage

  lux = lightMeter.readLightLevel();
  if (isnan(lux)) {
    Serial.println("Failed to read light level!");
  }

  digitalWrite(LED, LOW);
  digitalWrite(LED2, LOW);
  digitalWrite(rele, LOW);

  if (moisture <= 70) {
    digitalWrite(LED, HIGH);
    digitalWrite(rele, HIGH);
    Serial.println("Moist soil");
  } else {
    digitalWrite(LED2, HIGH);
    digitalWrite(rele, LOW);
    Serial.println("Dry soil");
  }
}

void sendSensorDataToMQTT(String plantaNomeReal, String time) {
  String data = "Temp: " + String(temp) + "C, Hum: " + String(humidity) + "%, Light: " + String(lux) + "lux, Soil: " + String(moisture) + "%, Depth: " + String(moisture2) + "%, Planta: " + plantaNomeReal + ", Time: " + time;
  mqtt_client.publish(mqtt_topic, data.c_str());
}

void printValues() {
  Serial.print("Temperature: ");
  Serial.print(temp);
  Serial.print(" *C, Humidity: ");
  Serial.print(humidity);
  Serial.print("%, Moisture: ");
  Serial.print(moisture);
  Serial.print("%, Light: ");
  Serial.print(lux);
  Serial.print(" lx, Depth: ");
  Serial.print(moisture2);
  Serial.print("%, Time: 16 s, ");
  printLocalTime();
}

void printLocalTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return;
  }
  Serial.print("Current time: ");
  Serial.print(&timeinfo, "%Y-%m-%d %H:%M:%S");
  Serial.println();
}

bool verifyLocalTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return false;
  }
  Serial.println("Date and time verified");
  if (timeinfo.tm_year < (2016 - 1900)) {
    Serial.println("Invalid date! Restarting...");
    ESP.restart();
    return false;
  }
  return true;
}


