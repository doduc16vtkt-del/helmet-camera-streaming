/**
 * Configuration file for Helmet Camera RF System
 * Tệp cấu hình cho hệ thống Camera Mũ Bảo Hiểm RF
 */

#ifndef CONFIG_H
#define CONFIG_H

// ============================================
// System Configuration / Cấu hình hệ thống
// ============================================

#define VERSION "1.0.0"
#define DEVICE_ID "HELMET_01"  // Unique device identifier

// ============================================
// Debug Configuration / Cấu hình debug
// ============================================

#define DEBUG_ENABLE 1
#define SERIAL_BAUD 115200

#if DEBUG_ENABLE
  #define DEBUG_PRINT(x) Serial.print(x)
  #define DEBUG_PRINTLN(x) Serial.println(x)
#else
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTLN(x)
#endif

// ============================================
// Camera Configuration / Cấu hình camera
// ============================================

#define CAMERA_MODEL_AI_THINKER  // ESP32-CAM board type

// Camera resolution - adjust based on needs
#define CAMERA_FRAME_SIZE FRAMESIZE_VGA  // 640x480
// Other options: FRAMESIZE_QVGA (320x240), FRAMESIZE_CIF (400x296)

#define CAMERA_JPEG_QUALITY 10  // 10-63, lower means higher quality
#define CAMERA_FB_COUNT 2       // Number of frame buffers

// ============================================
// RF Video Transmitter Configuration
// Cấu hình phát video RF 5.8GHz
// ============================================

#define RF_VIDEO_CHANNEL 1      // Channel 1-8
#define RF_VIDEO_POWER 25       // Power in mW (25, 200, 600)
#define RF_VIDEO_BAND 'E'       // Band: A, B, E, F, R, L

// 5.8GHz Channel Frequencies (MHz)
// Band E commonly used for FPV
const uint16_t RF_CHANNEL_FREQ[] = {
  5705, 5685, 5665, 5645,  // Channels 1-4
  5885, 5905, 5925, 5945   // Channels 5-8
};

// ============================================
// RF Telemetry Configuration (nRF24L01+)
// Cấu hình telemetry RF 2.4GHz
// ============================================

#define RF_TELEMETRY_CHANNEL 76     // nRF24 channel (0-125)
#define RF_TELEMETRY_RATE RF24_250KBPS  // Data rate
#define RF_TELEMETRY_PA_LEVEL RF24_PA_MAX   // Power level

// nRF24L01+ Pin Configuration for ESP32-CAM
// Note: Some pins may conflict with camera, adjust as needed
#define NRF24_CE_PIN 2
#define NRF24_CSN_PIN 14
#define NRF24_SCK_PIN 12
#define NRF24_MOSI_PIN 13
#define NRF24_MISO_PIN 15

// Telemetry addressing
const uint8_t TELEMETRY_ADDRESS[6] = "HLMT1";  // 5 characters + null
#define TELEMETRY_INTERVAL 1000  // Send telemetry every 1000ms

// ============================================
// Power Management Configuration
// Cấu hình quản lý nguồn
// ============================================

#define BATTERY_ADC_PIN 33      // ADC pin for battery voltage reading
#define BATTERY_TYPE_3S 1       // 3S LiPo (11.1V nominal)

// Voltage divider for battery reading (adjust based on resistors)
#define VOLTAGE_DIVIDER_RATIO 4.2  // R1=33k, R2=10k => (33+10)/10 = 4.3

// Battery voltage thresholds (for 3S LiPo)
#define BATTERY_MAX_VOLTAGE 12.6    // Fully charged
#define BATTERY_NOMINAL_VOLTAGE 11.1 // Nominal
#define BATTERY_LOW_VOLTAGE 10.5    // Low warning
#define BATTERY_CRITICAL_VOLTAGE 9.9 // Critical shutdown

// Power management timing
#define POWER_CHECK_INTERVAL 5000   // Check every 5 seconds
#define LOW_POWER_MODE_ENABLE 1     // Enable power saving features

// ============================================
// GPIO Pin Configuration
// Cấu hình chân GPIO
// ============================================

#define STATUS_LED_PIN 4        // Status LED (also flash LED on ESP32-CAM)
#define STATUS_BLINK_INTERVAL 2000  // Blink every 2 seconds when running

// ============================================
// System Timing Configuration
// Cấu hình thời gian hệ thống
// ============================================

#define WATCHDOG_TIMEOUT 30000  // Watchdog timeout in ms
#define MAX_ERROR_COUNT 100     // Max consecutive errors before restart

// ============================================
// Error Codes / Mã lỗi
// ============================================

#define ERROR_NONE 0
#define ERROR_CAMERA_INIT 1
#define ERROR_RF_TELEMETRY_INIT 2
#define ERROR_RF_VIDEO_INIT 3
#define ERROR_POWER_INIT 4
#define ERROR_BATTERY_CRITICAL 5
#define ERROR_CAMERA_CAPTURE 6

// Alert codes for telemetry
#define ALERT_BATTERY_LOW 10
#define ALERT_BATTERY_CRITICAL 11
#define ALERT_HIGH_TEMPERATURE 12
#define ALERT_SIGNAL_WEAK 13

// ============================================
// Camera Pin Definition for AI-Thinker ESP32-CAM
// Định nghĩa chân camera cho ESP32-CAM
// ============================================

#ifdef CAMERA_MODEL_AI_THINKER
  #define PWDN_GPIO_NUM     32
  #define RESET_GPIO_NUM    -1
  #define XCLK_GPIO_NUM      0
  #define SIOD_GPIO_NUM     26
  #define SIOC_GPIO_NUM     27
  
  #define Y9_GPIO_NUM       35
  #define Y8_GPIO_NUM       34
  #define Y7_GPIO_NUM       39
  #define Y6_GPIO_NUM       36
  #define Y5_GPIO_NUM       21
  #define Y4_GPIO_NUM       19
  #define Y3_GPIO_NUM       18
  #define Y2_GPIO_NUM        5
  #define VSYNC_GPIO_NUM    25
  #define HREF_GPIO_NUM     23
  #define PCLK_GPIO_NUM     22
#endif

// ============================================
// Memory Configuration
// Cấu hình bộ nhớ
// ============================================

#define FRAME_BUFFER_SIZE (640 * 480 * 2)  // Max frame buffer size

#endif // CONFIG_H
