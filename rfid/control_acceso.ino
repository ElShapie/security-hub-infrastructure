// Ejemplo exclusivo para Arduino Uno y lector MFRC522 por SPI.
// Confirmar modelo, alimentación y adaptación de niveles antes del montaje.
#include <SPI.h>
#include <MFRC522.h>

const byte SS_PIN = 10;
const byte RST_PIN = 9;
const byte LED_OK = 4;
const byte LED_NO = 5;
MFRC522 lector(SS_PIN, RST_PIN);
String modo = "ENTRADA";
String ultimoUID = "";
unsigned long ultimaLectura = 0;

const String tarjetas[4] = {
  "PENDIENTE_UID_INGENIERO",
  "PENDIENTE_UID_ADMIN",
  "PENDIENTE_UID_GUARDIA",
  "PENDIENTE_UID_AUDITOR"
};
const String empleados[4] = {"LAB-INGENIERO", "LAB-ADMIN", "LAB-GUARDIA", "LAB-AUDITOR"};

void setup() {
  Serial.begin(9600);
  SPI.begin();
  lector.PCD_Init();
  pinMode(LED_OK, OUTPUT);
  pinMode(LED_NO, OUTPUT);
  digitalWrite(LED_OK, LOW);
  digitalWrite(LED_NO, LOW);
  Serial.println("INFO,LISTO,ENTRADA,E=ENTRADA S=SALIDA");
}

void loop() {
  if (Serial.available()) {
    char orden = Serial.read();
    if (orden == 'E' || orden == 'e') modo = "ENTRADA";
    if (orden == 'S' || orden == 's') modo = "SALIDA";
  }
  if (!lector.PICC_IsNewCardPresent() || !lector.PICC_ReadCardSerial()) return;
  String uid = "";
  for (byte i = 0; i < lector.uid.size; i++) {
    if (lector.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(lector.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  bool repetida = uid == ultimoUID && millis() - ultimaLectura < 3000;
  if (!repetida) {
    ultimoUID = uid;
    ultimaLectura = millis();
    int indice = -1;
    for (int i = 0; i < 4; i++) if (uid == tarjetas[i]) indice = i;
    digitalWrite(LED_OK, indice >= 0 ? HIGH : LOW);
    digitalWrite(LED_NO, indice >= 0 ? LOW : HIGH);
    Serial.print(modo); Serial.print(",");
    Serial.print(uid); Serial.print(",");
    Serial.print(indice >= 0 ? "PERMITIDO" : "DENEGADO"); Serial.print(",");
    Serial.println(indice >= 0 ? empleados[indice] : "DESCONOCIDO");
    delay(1200);
    digitalWrite(LED_OK, LOW);
    digitalWrite(LED_NO, LOW);
  }
  lector.PICC_HaltA();
  lector.PCD_StopCrypto1();
}
