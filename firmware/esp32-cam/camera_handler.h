/**
 * Camera Handler Module
 * Module xử lý camera
 */

#ifndef CAMERA_HANDLER_H
#define CAMERA_HANDLER_H

#include <Arduino.h>
#include "esp_camera.h"
#include "config.h"

class CameraHandler {
private:
  camera_fb_t* frameBuffer;
  bool initialized;
  uint32_t captureCount;
  uint32_t errorCount;

public:
  CameraHandler();
  ~CameraHandler();
  
  /**
   * Initialize camera
   * Khởi tạo camera
   */
  bool begin();
  
  /**
   * Capture a frame from camera
   * Chụp một khung hình từ camera
   */
  bool captureFrame();
  
  /**
   * Get current frame buffer
   * Lấy buffer khung hình hiện tại
   */
  uint8_t* getFrameBuffer();
  
  /**
   * Get current frame size
   * Lấy kích thước khung hình hiện tại
   */
  size_t getFrameSize();
  
  /**
   * Release frame buffer
   * Giải phóng buffer khung hình
   */
  void releaseFrame();
  
  /**
   * Get camera status
   * Lấy trạng thái camera
   */
  bool isInitialized() { return initialized; }
  
  /**
   * Get capture statistics
   * Lấy thống kê chụp ảnh
   */
  uint32_t getCaptureCount() { return captureCount; }
  uint32_t getErrorCount() { return errorCount; }
  
  /**
   * Adjust camera settings
   * Điều chỉnh cài đặt camera
   */
  void setBrightness(int level);  // -2 to 2
  void setContrast(int level);    // -2 to 2
  void setSaturation(int level);  // -2 to 2
  
private:
  /**
   * Configure camera pins and settings
   * Cấu hình chân và cài đặt camera
   */
  void configureCamera(camera_config_t& config);
};

#endif // CAMERA_HANDLER_H
