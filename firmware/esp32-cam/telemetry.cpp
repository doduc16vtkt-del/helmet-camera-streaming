/**
 * Telemetry Implementation
 * Triển khai module telemetry
 */

#include "telemetry.h"

Telemetry::Telemetry() {
  radio = nullptr;
  initialized = false;
  packetsSent = 0;
  packetsFailed = 0;
}

Telemetry::~Telemetry() {
  if (radio) {
    delete radio;
  }
}

bool Telemetry::begin() {
  // Initialize SPI for nRF24L01+
  // Note: ESP32-CAM has limited free pins, may need to share SPI with other peripherals
  
  // Create RF24 object
  radio = new RF24(NRF24_CE_PIN, NRF24_CSN_PIN);
  
  // Initialize SPI
  SPI.begin(NRF24_SCK_PIN, NRF24_MISO_PIN, NRF24_MOSI_PIN, NRF24_CSN_PIN);
  
  // Initialize radio
  if (!radio->begin()) {
    DEBUG_PRINTLN("nRF24L01+ initialization failed!");
    return false;
  }
  
  configureRadio();
  
  initialized = true;
  DEBUG_PRINTLN("Telemetry system initialized (nRF24L01+)");
  
  return true;
}

void Telemetry::configureRadio() {
  // Set power level
  radio->setPALevel(RF_TELEMETRY_PA_LEVEL);
  
  // Set data rate
  radio->setDataRate(RF_TELEMETRY_RATE);
  
  // Set channel
  radio->setChannel(RF_TELEMETRY_CHANNEL);
  
  // Set retry parameters
  radio->setRetries(5, 15);  // 5*250us delay, 15 retries
  
  // Set payload size
  radio->setPayloadSize(sizeof(TelemetryData));
  
  // Enable auto-acknowledgment
  radio->setAutoAck(true);
  
  // Open writing pipe
  radio->openWritingPipe(TELEMETRY_ADDRESS);
  
  // Stop listening (we're transmitter only)
  radio->stopListening();
  
  DEBUG_PRINT("nRF24 configured - Channel: ");
  DEBUG_PRINT(RF_TELEMETRY_CHANNEL);
  DEBUG_PRINT(", Data Rate: ");
  DEBUG_PRINTLN(RF_TELEMETRY_RATE == RF24_250KBPS ? "250kbps" : 
                RF_TELEMETRY_RATE == RF24_1MBPS ? "1Mbps" : "2Mbps");
}

bool Telemetry::sendData(const TelemetryData& data) {
  if (!initialized) {
    return false;
  }
  
  // Create a copy of data to add checksum
  TelemetryData packet = data;
  
  // Calculate and add checksum
  packet.checksum = calculateChecksum((uint8_t*)&packet, sizeof(TelemetryData) - 1);
  
  // Send packet
  bool success = radio->write(&packet, sizeof(TelemetryData));
  
  if (success) {
    packetsSent++;
  } else {
    packetsFailed++;
    DEBUG_PRINTLN("Telemetry transmission failed");
  }
  
  return success;
}

bool Telemetry::sendDeviceInfo(const char* deviceId, const char* version) {
  if (!initialized) {
    return false;
  }
  
  // Create a simple info packet
  struct {
    char type[8];
    char deviceId[16];
    char version[16];
    uint8_t checksum;
  } infoPacket;
  
  strncpy(infoPacket.type, "INFO", 8);
  strncpy(infoPacket.deviceId, deviceId, 16);
  strncpy(infoPacket.version, version, 16);
  infoPacket.checksum = calculateChecksum((uint8_t*)&infoPacket, sizeof(infoPacket) - 1);
  
  bool success = radio->write(&infoPacket, sizeof(infoPacket));
  
  if (success) {
    packetsSent++;
    DEBUG_PRINTLN("Device info sent");
  } else {
    packetsFailed++;
  }
  
  return success;
}

bool Telemetry::sendAlert(uint8_t alertCode) {
  if (!initialized) {
    return false;
  }
  
  // Create alert packet
  struct {
    char type[8];
    uint8_t alertCode;
    uint32_t timestamp;
    uint8_t checksum;
  } alertPacket;
  
  strncpy(alertPacket.type, "ALERT", 8);
  alertPacket.alertCode = alertCode;
  alertPacket.timestamp = millis();
  alertPacket.checksum = calculateChecksum((uint8_t*)&alertPacket, sizeof(alertPacket) - 1);
  
  bool success = radio->write(&alertPacket, sizeof(alertPacket));
  
  if (success) {
    packetsSent++;
    DEBUG_PRINT("Alert sent: ");
    DEBUG_PRINTLN(alertCode);
  } else {
    packetsFailed++;
  }
  
  return success;
}

uint8_t Telemetry::calculateChecksum(const uint8_t* data, size_t length) {
  uint8_t checksum = 0;
  for (size_t i = 0; i < length; i++) {
    checksum ^= data[i];
  }
  return checksum;
}
