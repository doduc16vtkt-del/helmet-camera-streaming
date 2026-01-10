/**
 * Power Management Module Header
 * Module quản lý nguồn điện
 */

#ifndef POWER_MANAGEMENT_H
#define POWER_MANAGEMENT_H

#include <Arduino.h>
#include "config.h"

class PowerManagement {
private:
  float currentVoltage;
  uint8_t batteryPercent;
  float temperature;
  bool lowPowerMode;
  uint32_t lastVoltageCheck;

public:
  PowerManagement();
  
  /**
   * Initialize power management
   * Khởi tạo quản lý nguồn
   */
  bool begin();
  
  /**
   * Read battery voltage
   * Đọc điện áp pin
   */
  float getBatteryVoltage();
  
  /**
   * Get battery percentage (0-100%)
   * Lấy phần trăm pin (0-100%)
   */
  uint8_t getBatteryPercent();
  
  /**
   * Get temperature (if sensor available)
   * Lấy nhiệt độ (nếu có cảm biến)
   */
  float getTemperature();
  
  /**
   * Check if battery is low
   * Kiểm tra pin yếu
   */
  bool isBatteryLow();
  
  /**
   * Check if battery is critical
   * Kiểm tra pin nguy hiểm
   */
  bool isBatteryCritical();
  
  /**
   * Enter low power mode
   * Vào chế độ tiết kiệm pin
   */
  void enterLowPowerMode();
  
  /**
   * Exit low power mode
   * Thoát chế độ tiết kiệm pin
   */
  void exitLowPowerMode();
  
  /**
   * Shutdown system
   * Tắt hệ thống
   */
  void shutdown();
  
  /**
   * Update power status
   * Cập nhật trạng thái nguồn
   */
  void update();
  
private:
  /**
   * Read ADC value and convert to voltage
   * Đọc giá trị ADC và chuyển sang điện áp
   */
  float readVoltage();
  
  /**
   * Calculate battery percentage from voltage
   * Tính phần trăm pin từ điện áp
   */
  uint8_t calculatePercent(float voltage);
};

#endif // POWER_MANAGEMENT_H
