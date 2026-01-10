#!/usr/bin/env python3
"""
RF Link Testing Tool
Công cụ kiểm tra đường truyền RF

Tests RF link quality and telemetry communication
Kiểm tra chất lượng đường truyền RF và truyền thông telemetry
"""

import sys
import time
import argparse
try:
    from RF24 import RF24, RF24_PA_MAX, RF24_250KBPS
    RF24_AVAILABLE = True
except ImportError:
    print("Warning: RF24 library not available. Install with: pip3 install RF24")
    RF24_AVAILABLE = False

def test_rf_link(channel=76, timeout=10):
    """Test RF link by listening for packets"""
    
    if not RF24_AVAILABLE:
        print("ERROR: RF24 library required")
        return False
    
    print("=" * 60)
    print("RF Link Testing Tool")
    print("Công cụ Kiểm tra Đường truyền RF")
    print("=" * 60)
    print(f"\nChannel: {channel}")
    print(f"Timeout: {timeout} seconds\n")
    
    try:
        # GPIO pin configuration (Raspberry Pi BCM numbering)
        CE_PIN = 22
        CSN_PIN = 0
        SPI_SPEED = 8000000
        
        # Initialize radio
        radio = RF24(CE_PIN, CSN_PIN, SPI_SPEED)
        
        if not radio.begin():
            print("ERROR: Failed to initialize nRF24L01+")
            return False
        
        # Configure radio
        radio.setPALevel(RF24_PA_MAX)
        radio.setDataRate(RF24_250KBPS)
        radio.setChannel(channel)
        radio.enableDynamicPayloads()
        radio.setAutoAck(True)
        
        # Open reading pipe
        address = b"HLMT1"
        radio.openReadingPipe(1, address)
        radio.startListening()
        
        print("✓ nRF24L01+ initialized successfully")
        print(f"✓ Listening on channel {channel}")
        print(f"✓ Address: {address.decode()}")
        print("\nWaiting for packets...\n")
        
        # Statistics
        start_time = time.time()
        packets_received = 0
        last_packet_time = start_time
        
        while (time.time() - start_time) < timeout:
            if radio.available():
                # Read payload
                payload_size = radio.getDynamicPayloadSize()
                payload = radio.read(payload_size)
                
                packets_received += 1
                last_packet_time = time.time()
                
                # Parse and display
                try:
                    message = payload.decode('utf-8')
                    print(f"[{packets_received:03d}] Received: {message}")
                    
                    # Parse telemetry
                    if message.startswith('TELEM:'):
                        parts = message.split(':')
                        if len(parts) >= 6:
                            print(f"      Device: {parts[1]}")
                            print(f"      Battery: {parts[3]}% ({parts[2]}V)")
                            print(f"      Temperature: {parts[4]}°C")
                            print(f"      Uptime: {parts[5]}s")
                    
                except Exception as e:
                    print(f"[{packets_received:03d}] Received {payload_size} bytes (binary)")
                
                print()
            
            time.sleep(0.01)
        
        # Results
        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print("Test Results / Kết quả kiểm tra")
        print("=" * 60)
        print(f"Duration: {elapsed:.1f} seconds")
        print(f"Packets received: {packets_received}")
        print(f"Average rate: {packets_received/elapsed:.2f} packets/sec")
        
        if packets_received > 0:
            print(f"Last packet: {time.time() - last_packet_time:.1f}s ago")
            print("\n✓ RF link is working!")
            return True
        else:
            print("\n✗ No packets received")
            print("\nTroubleshooting:")
            print("1. Check camera unit is powered on")
            print("2. Verify same channel on TX and RX")
            print("3. Check nRF24L01+ connections")
            print("4. Try moving closer (< 10m for initial test)")
            return False
    
    except Exception as e:
        print(f"\nERROR: {e}")
        return False
    finally:
        if RF24_AVAILABLE and 'radio' in locals():
            radio.stopListening()

def test_transmit(channel=76, count=10):
    """Test transmission by sending test packets"""
    
    if not RF24_AVAILABLE:
        print("ERROR: RF24 library required")
        return False
    
    print("=" * 60)
    print("RF Transmission Test")
    print("=" * 60)
    
    try:
        # Initialize radio
        radio = RF24(22, 0, 8000000)
        
        if not radio.begin():
            print("ERROR: Failed to initialize nRF24L01+")
            return False
        
        # Configure for transmission
        radio.setPALevel(RF24_PA_MAX)
        radio.setDataRate(RF24_250KBPS)
        radio.setChannel(channel)
        radio.enableDynamicPayloads()
        radio.setRetries(5, 15)
        
        # Open writing pipe
        address = b"HLMT1"
        radio.openWritingPipe(address)
        radio.stopListening()
        
        print(f"✓ Transmitting on channel {channel}")
        print(f"✓ Sending {count} test packets\n")
        
        success_count = 0
        
        for i in range(count):
            # Create test packet
            message = f"TEST:{i}:{time.time():.2f}"
            payload = message.encode('utf-8')
            
            # Send
            if radio.write(payload):
                success_count += 1
                print(f"[{i+1:02d}] ✓ Sent: {message}")
            else:
                print(f"[{i+1:02d}] ✗ Failed")
            
            time.sleep(0.5)
        
        print(f"\nSuccess rate: {success_count}/{count} ({success_count/count*100:.0f}%)")
        
        return success_count > 0
    
    except Exception as e:
        print(f"\nERROR: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='RF Link Testing Tool / Công cụ Kiểm tra Đường truyền RF'
    )
    parser.add_argument(
        '--channel', '-c',
        type=int,
        default=76,
        help='RF channel (0-125), default: 76'
    )
    parser.add_argument(
        '--timeout', '-t',
        type=int,
        default=10,
        help='Test timeout in seconds, default: 10'
    )
    parser.add_argument(
        '--transmit', '-tx',
        action='store_true',
        help='Test transmission instead of reception'
    )
    parser.add_argument(
        '--count', '-n',
        type=int,
        default=10,
        help='Number of packets to transmit, default: 10'
    )
    
    args = parser.parse_args()
    
    if args.transmit:
        success = test_transmit(args.channel, args.count)
    else:
        success = test_rf_link(args.channel, args.timeout)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
