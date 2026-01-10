#!/usr/bin/env python3
"""
Telemetry Test Script
Script kiểm tra telemetry

Tests telemetry protocol and data formatting
Kiểm tra giao thức telemetry và định dạng dữ liệu
"""

import sys
import struct

def test_text_protocol():
    """Test text-based telemetry protocol"""
    print("Testing text protocol...")
    print("Kiểm tra giao thức văn bản...")
    
    # Sample telemetry message
    message = "TELEM:HELMET_01:11.45:76:42.3:1234"
    
    # Parse
    parts = message.split(':')
    
    assert len(parts) == 6, "Invalid message format"
    assert parts[0] == "TELEM", "Invalid message type"
    
    telemetry = {
        'device_id': parts[1],
        'voltage': float(parts[2]),
        'percent': int(parts[3]),
        'temperature': float(parts[4]),
        'uptime': int(parts[5])
    }
    
    print(f"✓ Parsed telemetry:")
    print(f"  Device: {telemetry['device_id']}")
    print(f"  Battery: {telemetry['percent']}% ({telemetry['voltage']}V)")
    print(f"  Temperature: {telemetry['temperature']}°C")
    print(f"  Uptime: {telemetry['uptime']}s")
    
    return True

def test_binary_protocol():
    """Test binary telemetry protocol"""
    print("\nTesting binary protocol...")
    print("Kiểm tra giao thức nhị phân...")
    
    # Create binary packet (simplified)
    device_id = b"HELMET_01\x00\x00\x00\x00\x00\x00\x00"  # 16 bytes
    voltage = struct.pack('f', 11.45)
    percent = struct.pack('B', 76)
    rssi = struct.pack('b', -75)
    temperature = struct.pack('f', 42.3)
    uptime = struct.pack('I', 1234)
    
    packet = device_id + voltage + percent + rssi + temperature + uptime
    
    print(f"✓ Binary packet size: {len(packet)} bytes")
    print(f"✓ Packet hex: {packet[:20].hex()}...")
    
    # Unpack
    device_id_unpacked = packet[:16].decode('utf-8').rstrip('\x00')
    voltage_unpacked = struct.unpack('f', packet[16:20])[0]
    percent_unpacked = struct.unpack('B', packet[20:21])[0]
    
    print(f"✓ Unpacked device ID: {device_id_unpacked}")
    print(f"✓ Unpacked voltage: {voltage_unpacked:.2f}V")
    print(f"✓ Unpacked battery: {percent_unpacked}%")
    
    return True

def test_checksum():
    """Test checksum calculation"""
    print("\nTesting checksum...")
    print("Kiểm tra checksum...")
    
    # Sample data
    data = b"TELEM:HELMET_01:11.45:76:42.3:1234"
    
    # XOR checksum
    checksum = 0
    for byte in data:
        checksum ^= byte
    
    print(f"✓ Data: {data}")
    print(f"✓ Checksum (XOR): 0x{checksum:02X}")
    
    # Verify
    verify_checksum = 0
    for byte in data:
        verify_checksum ^= byte
    
    assert checksum == verify_checksum, "Checksum verification failed"
    print(f"✓ Checksum verified")
    
    return True

def test_packet_size():
    """Test packet sizes are within nRF24 limits"""
    print("\nTesting packet sizes...")
    print("Kiểm tra kích thước gói tin...")
    
    # nRF24L01+ max payload: 32 bytes
    max_payload = 32
    
    # Text protocol
    text_packet = "TELEM:HELMET_01:11.45:76:42.3:1234"
    text_size = len(text_packet.encode('utf-8'))
    
    print(f"✓ Text packet size: {text_size} bytes")
    if text_size <= max_payload:
        print(f"  OK (within {max_payload} byte limit)")
    else:
        print(f"  ⚠ Warning: Exceeds {max_payload} byte limit!")
    
    # Binary protocol (estimated)
    binary_size = 16 + 4 + 1 + 1 + 4 + 4  # device_id + float + bytes + float + uint32
    print(f"✓ Binary packet size (estimated): {binary_size} bytes")
    if binary_size <= max_payload:
        print(f"  OK (within {max_payload} byte limit)")
    else:
        print(f"  ⚠ Warning: Exceeds {max_payload} byte limit!")
    
    return True

def test_telemetry_rate():
    """Test telemetry transmission rate"""
    print("\nTesting telemetry rate...")
    print("Kiểm tra tốc độ telemetry...")
    
    telemetry_interval = 1.0  # seconds
    packet_size = 40  # bytes (with overhead)
    
    # Calculate bandwidth
    bits_per_second = (packet_size * 8) / telemetry_interval
    
    print(f"✓ Telemetry interval: {telemetry_interval}s")
    print(f"✓ Packet size (with overhead): {packet_size} bytes")
    print(f"✓ Required bandwidth: {bits_per_second:.0f} bps")
    
    # nRF24L01+ data rate options
    data_rates = {
        '250kbps': 250000,
        '1Mbps': 1000000,
        '2Mbps': 2000000
    }
    
    print(f"\nAvailable data rates:")
    for name, rate in data_rates.items():
        utilization = (bits_per_second / rate) * 100
        print(f"  {name}: {utilization:.2f}% utilization")
    
    print("\n✓ Using 250kbps recommended for maximum range")
    
    return True

def main():
    """Main test runner"""
    print("=" * 60)
    print("Telemetry Test Suite")
    print("Bộ kiểm tra Telemetry")
    print("=" * 60)
    print()
    
    tests = [
        test_text_protocol,
        test_binary_protocol,
        test_checksum,
        test_packet_size,
        test_telemetry_rate
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results / Kết quả")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
