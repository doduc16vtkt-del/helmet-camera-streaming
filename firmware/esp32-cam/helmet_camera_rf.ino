/**
 * Helmet Camera RF Streaming System - ESP32-CAM Firmware
 * Hệ thống truyền video từ camera mũ bảo hiểm qua RF
 * 
 * Hardware: ESP32-CAM + OV2640 Camera + nRF24L01+ + 5.8GHz Video TX
 * 
 * Copyright (c) 2024
 * License: MIT
 */

#include "config.h"
#include "camera_handler.h"
#include "rf_transmitter.h"
#include "telemetry.h"
#include "power_management.h"

// Global objects
CameraHandler camera;
RFTransmitter rfVideo;
Telemetry telemetry;
PowerManagement power;

// Timing variables
unsigned long lastTelemetryTime = 0;
unsigned long lastStatusTime = 0;
unsigned long lastPowerCheckTime = 0;

// System state
bool systemReady = false;
uint8_t errorCount = 0;

void setup() {
  // Initialize serial for debugging
  #if DEBUG_ENABLE
  Serial.begin(SERIAL_BAUD);
  delay(100);
  Serial.println("\n\n========================================");
  Serial.println("Helmet Camera RF System Starting...");
  Serial.println("Hệ thống Camera Mũ Bảo Hiểm RF");
  Serial.println("========================================\n");
  #endif

  // Initialize status LED
  pinMode(STATUS_LED_PIN, OUTPUT);
  blinkLED(3, 200); // 3 quick blinks

  // Initialize power management
  DEBUG_PRINTLN("Initializing power management...");
  if (!power.begin()) {
    DEBUG_PRINTLN("ERROR: Power management init failed!");
    errorHandler(ERROR_POWER_INIT);
  }
  
  // Check battery voltage
  float voltage = power.getBatteryVoltage();
  DEBUG_PRINT("Battery voltage: ");
  DEBUG_PRINT(voltage);
  DEBUG_PRINTLN(" V");
  
  if (voltage < BATTERY_CRITICAL_VOLTAGE) {
    DEBUG_PRINTLN("ERROR: Battery voltage critical!");
    errorHandler(ERROR_BATTERY_CRITICAL);
  }

  // Initialize camera
  DEBUG_PRINTLN("Initializing camera...");
  if (!camera.begin()) {
    DEBUG_PRINTLN("ERROR: Camera init failed!");
    errorHandler(ERROR_CAMERA_INIT);
  }
  DEBUG_PRINTLN("Camera initialized successfully");

  // Initialize RF telemetry
  DEBUG_PRINTLN("Initializing RF telemetry...");
  if (!telemetry.begin()) {
    DEBUG_PRINTLN("ERROR: RF telemetry init failed!");
    errorHandler(ERROR_RF_TELEMETRY_INIT);
  }
  DEBUG_PRINTLN("RF telemetry initialized successfully");

  // Initialize RF video transmitter
  DEBUG_PRINTLN("Initializing RF video transmitter...");
  if (!rfVideo.begin()) {
    DEBUG_PRINTLN("ERROR: RF video TX init failed!");
    errorHandler(ERROR_RF_VIDEO_INIT);
  }
  DEBUG_PRINTLN("RF video transmitter initialized");

  // Set RF video channel
  rfVideo.setChannel(RF_VIDEO_CHANNEL);
  rfVideo.setPower(RF_VIDEO_POWER);
  
  DEBUG_PRINT("RF Video Channel: ");
  DEBUG_PRINTLN(RF_VIDEO_CHANNEL);
  DEBUG_PRINT("RF Video Power: ");
  DEBUG_PRINT(RF_VIDEO_POWER);
  DEBUG_PRINTLN(" mW");

  // Send initial telemetry
  telemetry.sendDeviceInfo(DEVICE_ID, VERSION);
  
  systemReady = true;
  blinkLED(5, 100); // 5 fast blinks to indicate ready
  
  DEBUG_PRINTLN("\n========================================");
  DEBUG_PRINTLN("System Ready - Video Streaming Active");
  DEBUG_PRINTLN("Hệ thống sẵn sàng - Đang truyền video");
  DEBUG_PRINTLN("========================================\n");
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check if system is ready
  if (!systemReady) {
    delay(1000);
    return;
  }

  // Capture and stream video frame
  if (camera.captureFrame()) {
    // Camera captures directly to analog video output
    // or digital encoding if using digital RF transmitter
    rfVideo.transmitFrame(camera.getFrameBuffer(), camera.getFrameSize());
  } else {
    errorCount++;
    if (errorCount > MAX_ERROR_COUNT) {
      DEBUG_PRINTLN("ERROR: Too many camera failures, restarting...");
      ESP.restart();
    }
  }

  // Send telemetry data periodically
  if (currentTime - lastTelemetryTime >= TELEMETRY_INTERVAL) {
    lastTelemetryTime = currentTime;
    
    // Collect telemetry data
    TelemetryData data;
    data.deviceId = DEVICE_ID;
    data.batteryVoltage = power.getBatteryVoltage();
    data.batteryPercent = power.getBatteryPercent();
    data.rssi = rfVideo.getRSSI();
    data.temperature = power.getTemperature();
    data.uptime = millis() / 1000; // seconds
    data.errorCount = errorCount;
    
    // Send telemetry
    if (telemetry.sendData(data)) {
      errorCount = max(0, errorCount - 1); // Decrease error count on success
    } else {
      errorCount++;
    }
    
    #if DEBUG_ENABLE
    DEBUG_PRINT("Telemetry sent - Battery: ");
    DEBUG_PRINT(data.batteryPercent);
    DEBUG_PRINT("% (");
    DEBUG_PRINT(data.batteryVoltage);
    DEBUG_PRINT("V), Temp: ");
    DEBUG_PRINT(data.temperature);
    DEBUG_PRINT("C, Uptime: ");
    DEBUG_PRINT(data.uptime);
    DEBUG_PRINTLN("s");
    #endif
  }

  // Check power status
  if (currentTime - lastPowerCheckTime >= POWER_CHECK_INTERVAL) {
    lastPowerCheckTime = currentTime;
    
    float voltage = power.getBatteryVoltage();
    
    // Critical voltage - shutdown
    if (voltage < BATTERY_CRITICAL_VOLTAGE) {
      DEBUG_PRINTLN("CRITICAL: Battery voltage too low, shutting down...");
      telemetry.sendAlert(ALERT_BATTERY_CRITICAL);
      delay(100);
      power.shutdown();
    }
    // Low voltage warning
    else if (voltage < BATTERY_LOW_VOLTAGE) {
      DEBUG_PRINTLN("WARNING: Battery voltage low!");
      telemetry.sendAlert(ALERT_BATTERY_LOW);
      blinkLED(2, 500); // Slow blinks as warning
    }
  }

  // Status indicator blink
  if (currentTime - lastStatusTime >= STATUS_BLINK_INTERVAL) {
    lastStatusTime = currentTime;
    digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN));
  }

  // Small delay to prevent watchdog timeout
  delay(10);
}

/**
 * Blink LED pattern
 */
void blinkLED(int count, int delayMs) {
  for (int i = 0; i < count; i++) {
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(delayMs);
    digitalWrite(STATUS_LED_PIN, LOW);
    delay(delayMs);
  }
}

/**
 * Error handler - handle critical errors
 */
void errorHandler(int errorCode) {
  DEBUG_PRINT("CRITICAL ERROR: ");
  DEBUG_PRINTLN(errorCode);
  
  // Send error telemetry if possible
  telemetry.sendAlert(errorCode);
  
  // Blink error pattern
  while (true) {
    for (int i = 0; i < errorCode; i++) {
      digitalWrite(STATUS_LED_PIN, HIGH);
      delay(200);
      digitalWrite(STATUS_LED_PIN, LOW);
      delay(200);
    }
    delay(2000);
  }
}
