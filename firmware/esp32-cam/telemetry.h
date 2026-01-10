/**
 * Telemetry Module Header
 * Module telemetry qua RF 2.4GHz
 */

#ifndef TELEMETRY_H
#define TELEMETRY_H

#include <Arduino.h>
#include <SPI.h>
#include <RF24.h>
#include "config.h"

// Telemetry data structure
struct TelemetryData {
  char deviceId[16];
  float batteryVoltage;
  uint8_t batteryPercent;
  int8_t rssi;
  float temperature;
  uint32_t uptime;
  uint16_t errorCount;
  uint8_t checksum;
};

class Telemetry {
private:
  RF24* radio;
  bool initialized;
  uint32_t packetsSent;
  uint32_t packetsFailed;

public:
  Telemetry();
  ~Telemetry();
  
  /**
   * Initialize telemetry system (nRF24L01+)
   * Khởi tạo hệ thống telemetry
   */
  bool begin();
  
  /**
   * Send telemetry data
   * Gửi dữ liệu telemetry
   */
  bool sendData(const TelemetryData& data);
  
  /**
   * Send device information
   * Gửi thông tin thiết bị
   */
  bool sendDeviceInfo(const char* deviceId, const char* version);
  
  /**
   * Send alert/warning
   * Gửi cảnh báo
   */
  bool sendAlert(uint8_t alertCode);
  
  /**
   * Get statistics
   * Lấy thống kê
   */
  uint32_t getPacketsSent() { return packetsSent; }
  uint32_t getPacketsFailed() { return packetsFailed; }
  
  /**
   * Check if initialized
   * Kiểm tra đã khởi tạo chưa
   */
  bool isInitialized() { return initialized; }
  
private:
  /**
   * Calculate checksum for data integrity
   * Tính checksum cho tính toàn vẹn dữ liệu
   */
  uint8_t calculateChecksum(const uint8_t* data, size_t length);
  
  /**
   * Configure nRF24L01+ module
   * Cấu hình module nRF24L01+
   */
  void configureRadio();
};

#endif // TELEMETRY_H
