/**
 * Camera Handler Implementation
 * Triển khai module xử lý camera
 */

#include "camera_handler.h"

CameraHandler::CameraHandler() {
  frameBuffer = nullptr;
  initialized = false;
  captureCount = 0;
  errorCount = 0;
}

CameraHandler::~CameraHandler() {
  if (frameBuffer) {
    esp_camera_fb_return(frameBuffer);
  }
}

bool CameraHandler::begin() {
  camera_config_t config;
  configureCamera(config);
  
  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    DEBUG_PRINT("Camera init failed with error 0x");
    DEBUG_PRINTLN(err);
    return false;
  }
  
  // Get camera sensor
  sensor_t* s = esp_camera_sensor_get();
  if (s == nullptr) {
    DEBUG_PRINTLN("Failed to get camera sensor");
    return false;
  }
  
  // Set initial camera settings
  s->set_framesize(s, CAMERA_FRAME_SIZE);
  s->set_quality(s, CAMERA_JPEG_QUALITY);
  
  // Adjust for better outdoor/indoor performance
  s->set_brightness(s, 0);     // -2 to 2
  s->set_contrast(s, 0);       // -2 to 2
  s->set_saturation(s, 0);     // -2 to 2
  s->set_whitebal(s, 1);       // White balance enable
  s->set_awb_gain(s, 1);       // Auto white balance gain enable
  s->set_wb_mode(s, 0);        // White balance mode
  s->set_exposure_ctrl(s, 1);  // Auto exposure enable
  s->set_aec2(s, 1);           // AEC DSP enable
  s->set_gain_ctrl(s, 1);      // Auto gain enable
  s->set_agc_gain(s, 0);       // AGC gain
  s->set_gainceiling(s, (gainceiling_t)0);  // Gain ceiling
  
  // Flip/mirror if needed
  s->set_hmirror(s, 0);        // Horizontal mirror
  s->set_vflip(s, 0);          // Vertical flip
  
  initialized = true;
  DEBUG_PRINTLN("Camera initialized successfully");
  
  return true;
}

void CameraHandler::configureCamera(camera_config_t& config) {
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Frame size and quality
  config.frame_size = CAMERA_FRAME_SIZE;
  config.jpeg_quality = CAMERA_JPEG_QUALITY;
  config.fb_count = CAMERA_FB_COUNT;
  
  // PSRAM configuration
  if (psramFound()) {
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.grab_mode = CAMERA_GRAB_LATEST;
  } else {
    config.fb_location = CAMERA_FB_IN_DRAM;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  }
}

bool CameraHandler::captureFrame() {
  if (!initialized) {
    return false;
  }
  
  // Release previous frame if exists
  if (frameBuffer) {
    esp_camera_fb_return(frameBuffer);
    frameBuffer = nullptr;
  }
  
  // Capture new frame
  frameBuffer = esp_camera_fb_get();
  
  if (!frameBuffer) {
    errorCount++;
    DEBUG_PRINTLN("Camera capture failed");
    return false;
  }
  
  captureCount++;
  return true;
}

uint8_t* CameraHandler::getFrameBuffer() {
  if (frameBuffer) {
    return frameBuffer->buf;
  }
  return nullptr;
}

size_t CameraHandler::getFrameSize() {
  if (frameBuffer) {
    return frameBuffer->len;
  }
  return 0;
}

void CameraHandler::releaseFrame() {
  if (frameBuffer) {
    esp_camera_fb_return(frameBuffer);
    frameBuffer = nullptr;
  }
}

void CameraHandler::setBrightness(int level) {
  sensor_t* s = esp_camera_sensor_get();
  if (s) {
    s->set_brightness(s, level);
  }
}

void CameraHandler::setContrast(int level) {
  sensor_t* s = esp_camera_sensor_get();
  if (s) {
    s->set_contrast(s, level);
  }
}

void CameraHandler::setSaturation(int level) {
  sensor_t* s = esp_camera_sensor_get();
  if (s) {
    s->set_saturation(s, level);
  }
}
