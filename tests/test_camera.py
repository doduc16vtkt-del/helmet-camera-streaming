#!/usr/bin/env python3
"""
Camera Test Script
Script kiểm tra camera

Tests camera functionality and configuration
Kiểm tra chức năng và cấu hình camera
"""

import sys
import yaml

def test_configuration():
    """Test configuration file loading"""
    print("Testing configuration file...")
    print("Kiểm tra tệp cấu hình...")
    
    try:
        with open('../../configs/camera_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        print("✓ Configuration loaded successfully")
        print(f"  Device ID: {config['rf_telemetry']['device_id']}")
        print(f"  Video Channel: {config['rf_video']['channel']}")
        print(f"  Telemetry Channel: {config['rf_telemetry']['channel']}")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_camera_params():
    """Test camera parameters are valid"""
    print("\nTesting camera parameters...")
    print("Kiểm tra tham số camera...")
    
    try:
        with open('../../configs/camera_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        camera = config.get('camera', {})
        
        # Check resolution
        resolution = camera.get('resolution', '640x480')
        width, height = map(int, resolution.split('x'))
        assert width > 0 and height > 0, "Invalid resolution"
        print(f"✓ Resolution: {resolution}")
        
        # Check FPS
        fps = camera.get('fps', 30)
        assert 1 <= fps <= 60, "FPS out of range"
        print(f"✓ FPS: {fps}")
        
        # Check RF channel
        rf_channel = config['rf_video']['channel']
        assert 1 <= rf_channel <= 8, "RF channel out of range"
        print(f"✓ RF Video Channel: {rf_channel}")
        
        return True
    except Exception as e:
        print(f"✗ Parameter test failed: {e}")
        return False

def test_pin_configuration():
    """Test pin configuration is valid"""
    print("\nTesting pin configuration...")
    print("Kiểm tra cấu hình chân...")
    
    try:
        with open('../../configs/camera_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        pins = config.get('pins', {})
        
        # Check nRF24 pins
        required_pins = ['nrf24_ce', 'nrf24_csn', 'nrf24_sck', 'nrf24_mosi', 'nrf24_miso']
        for pin_name in required_pins:
            pin = pins.get(pin_name)
            if pin is None or pin < 0:
                print(f"⚠ Warning: {pin_name} not configured")
            else:
                print(f"✓ {pin_name}: GPIO {pin}")
        
        return True
    except Exception as e:
        print(f"✗ Pin configuration test failed: {e}")
        return False

def main():
    """Main test runner"""
    print("=" * 60)
    print("Camera Unit Test Suite")
    print("Bộ kiểm tra thiết bị Camera")
    print("=" * 60)
    print()
    
    tests = [
        test_configuration,
        test_camera_params,
        test_pin_configuration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Test Results / Kết quả kiểm tra")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    if failed == 0:
        print("✓ All tests passed!")
        print("✓ Tất cả các kiểm tra đã vượt qua!")
        return 0
    else:
        print("✗ Some tests failed")
        print("✗ Một số kiểm tra thất bại")
        return 1

if __name__ == '__main__':
    sys.exit(main())
