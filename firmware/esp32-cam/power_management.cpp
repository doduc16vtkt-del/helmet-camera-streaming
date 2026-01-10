/**
 * Power Management Implementation
 * Triển khai module quản lý nguồn
 */

#include "power_management.h"

PowerManagement::PowerManagement() {
  currentVoltage = 0.0;
  batteryPercent = 0;
  temperature = 25.0;
  lowPowerMode = false;
  lastVoltageCheck = 0;
}

bool PowerManagement::begin() {
  // Configure ADC for battery voltage reading
  pinMode(BATTERY_ADC_PIN, INPUT);
  
  // Configure ADC
  analogReadResolution(12);  // 12-bit resolution (0-4095)
  analogSetAttenuation(ADC_11db);  // Full range 0-3.3V
  
  // Initial voltage reading
  currentVoltage = readVoltage();
  batteryPercent = calculatePercent(currentVoltage);
  
  DEBUG_PRINT("Power management initialized - Battery: ");
  DEBUG_PRINT(currentVoltage);
  DEBUG_PRINT("V (");
  DEBUG_PRINT(batteryPercent);
  DEBUG_PRINTLN("%)");
  
  return true;
}

float PowerManagement::readVoltage() {
  // Read ADC value (average of multiple readings for stability)
  const int numReadings = 10;
  uint32_t sum = 0;
  
  for (int i = 0; i < numReadings; i++) {
    sum += analogRead(BATTERY_ADC_PIN);
    delay(10);
  }
  
  float adcValue = sum / numReadings;
  
  // Convert ADC value to voltage
  // ESP32 ADC: 0-4095 corresponds to 0-3.3V
  // Then multiply by voltage divider ratio
  float voltage = (adcValue / 4095.0) * 3.3 * VOLTAGE_DIVIDER_RATIO;
  
  return voltage;
}

float PowerManagement::getBatteryVoltage() {
  unsigned long currentTime = millis();
  
  // Update voltage if enough time has passed
  if (currentTime - lastVoltageCheck >= POWER_CHECK_INTERVAL) {
    currentVoltage = readVoltage();
    batteryPercent = calculatePercent(currentVoltage);
    lastVoltageCheck = currentTime;
  }
  
  return currentVoltage;
}

uint8_t PowerManagement::calculatePercent(float voltage) {
  // Calculate battery percentage for 3S LiPo
  // 12.6V = 100%, 9.9V = 0%
  
  if (voltage >= BATTERY_MAX_VOLTAGE) {
    return 100;
  } else if (voltage <= BATTERY_CRITICAL_VOLTAGE) {
    return 0;
  }
  
  // Linear interpolation
  float range = BATTERY_MAX_VOLTAGE - BATTERY_CRITICAL_VOLTAGE;
  float percent = ((voltage - BATTERY_CRITICAL_VOLTAGE) / range) * 100.0;
  
  return (uint8_t)constrain(percent, 0, 100);
}

uint8_t PowerManagement::getBatteryPercent() {
  return batteryPercent;
}

float PowerManagement::getTemperature() {
  // ESP32 internal temperature sensor
  // Note: This is approximate and may not be very accurate
  #ifdef ESP32
  extern uint8_t temprature_sens_read();
  return (temprature_sens_read() - 32) / 1.8;
  #else
  return 25.0;  // Default value if not available
  #endif
}

bool PowerManagement::isBatteryLow() {
  return currentVoltage < BATTERY_LOW_VOLTAGE;
}

bool PowerManagement::isBatteryCritical() {
  return currentVoltage < BATTERY_CRITICAL_VOLTAGE;
}

void PowerManagement::enterLowPowerMode() {
  if (lowPowerMode) return;
  
  DEBUG_PRINTLN("Entering low power mode");
  
  // Reduce CPU frequency
  setCpuFrequencyMhz(80);  // Reduce from 240MHz to 80MHz
  
  // Reduce camera frame rate or quality
  // (Would be implemented in camera_handler)
  
  // Reduce RF transmission power if possible
  // (Would be implemented in rf_transmitter)
  
  lowPowerMode = true;
}

void PowerManagement::exitLowPowerMode() {
  if (!lowPowerMode) return;
  
  DEBUG_PRINTLN("Exiting low power mode");
  
  // Restore CPU frequency
  setCpuFrequencyMhz(240);
  
  lowPowerMode = false;
}

void PowerManagement::shutdown() {
  DEBUG_PRINTLN("Shutting down system...");
  
  // Turn off peripherals
  // camera.end();
  // rfVideo.end();
  // telemetry.end();
  
  // Deep sleep (will require reset to wake)
  esp_deep_sleep_start();
}

void PowerManagement::update() {
  // Update voltage reading
  getBatteryVoltage();
  
  // Check if we should enter/exit low power mode
  #if LOW_POWER_MODE_ENABLE
  if (isBatteryLow() && !lowPowerMode) {
    enterLowPowerMode();
  } else if (!isBatteryLow() && lowPowerMode) {
    exitLowPowerMode();
  }
  #endif
}
