/**
 * RF Transmitter Module Header
 * Module phát tín hiệu RF
 */

#ifndef RF_TRANSMITTER_H
#define RF_TRANSMITTER_H

#include <Arduino.h>
#include "config.h"

class RFTransmitter {
private:
  uint8_t currentChannel;
  uint8_t powerLevel;
  bool initialized;
  int8_t rssiValue;

public:
  RFTransmitter();
  
  /**
   * Initialize RF video transmitter
   * Khởi tạo bộ phát video RF
   */
  bool begin();
  
  /**
   * Set RF channel (1-8)
   * Đặt kênh RF (1-8)
   */
  void setChannel(uint8_t channel);
  
  /**
   * Set transmission power (25, 200, 600 mW)
   * Đặt công suất phát (25, 200, 600 mW)
   */
  void setPower(uint16_t power);
  
  /**
   * Transmit video frame
   * Phát khung hình video
   * Note: For analog video TX, this is mostly a passthrough
   * For digital, this would encode and transmit
   */
  bool transmitFrame(uint8_t* frameBuffer, size_t frameSize);
  
  /**
   * Get current RSSI (if supported by hardware)
   * Lấy RSSI hiện tại (nếu phần cứng hỗ trợ)
   */
  int8_t getRSSI();
  
  /**
   * Get current channel
   * Lấy kênh hiện tại
   */
  uint8_t getChannel() { return currentChannel; }
  
  /**
   * Check if initialized
   * Kiểm tra đã khởi tạo chưa
   */
  bool isInitialized() { return initialized; }
  
private:
  /**
   * Configure RF transmitter hardware
   * Cấu hình phần cứng phát RF
   */
  void configureTX();
  
  /**
   * Get frequency for channel
   * Lấy tần số cho kênh
   */
  uint16_t getFrequency(uint8_t channel);
};

#endif // RF_TRANSMITTER_H
