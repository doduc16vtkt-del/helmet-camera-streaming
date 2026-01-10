#!/usr/bin/env python3
"""
RF Channel Scanner
Công cụ quét kênh RF

Scans 5.8GHz channels for active video signals
Quét các kênh 5.8GHz để tìm tín hiệu video đang hoạt động
"""

import time
import sys

# Channel frequencies for 5.8GHz Band E
BAND_E_CHANNELS = {
    1: 5705,
    2: 5685,
    3: 5665,
    4: 5645,
    5: 5885,
    6: 5905,
    7: 5925,
    8: 5945
}

def scan_channels(duration=2):
    """
    Scan all channels and display results
    
    Note: This is a simulation. Real implementation would:
    1. Interface with RF receiver hardware
    2. Switch channels programmatically
    3. Measure RSSI for each channel
    """
    
    print("=" * 70)
    print("RF Channel Scanner / Công cụ Quét Kênh RF")
    print("5.8GHz Band E Channels")
    print("=" * 70)
    print()
    print(f"Scanning {len(BAND_E_CHANNELS)} channels...")
    print(f"Duration per channel: {duration}s")
    print()
    
    results = []
    
    for channel, frequency in sorted(BAND_E_CHANNELS.items()):
        print(f"Scanning Channel {channel} ({frequency} MHz)...", end=' ')
        sys.stdout.flush()
        
        # Simulate scanning
        time.sleep(duration)
        
        # Simulate RSSI (in real implementation, read from hardware)
        import random
        rssi = random.randint(-95, -60)  # Simulated RSSI
        signal_present = rssi > -85
        
        results.append({
            'channel': channel,
            'frequency': frequency,
            'rssi': rssi,
            'active': signal_present
        })
        
        if signal_present:
            print(f"✓ ACTIVE (RSSI: {rssi} dBm)")
        else:
            print(f"✗ No signal (RSSI: {rssi} dBm)")
    
    # Display summary
    print()
    print("=" * 70)
    print("Scan Results / Kết quả quét")
    print("=" * 70)
    print()
    print(f"{'Channel':<10} {'Frequency':<15} {'RSSI':<12} {'Status':<15}")
    print("-" * 70)
    
    active_count = 0
    
    for result in results:
        status = "ACTIVE ✓" if result['active'] else "No signal"
        if result['active']:
            active_count += 1
        
        print(f"{result['channel']:<10} {result['frequency']} MHz{'':<7} "
              f"{result['rssi']} dBm{'':<4} {status:<15}")
    
    print("-" * 70)
    print(f"\nActive channels: {active_count}/{len(results)}")
    print()
    
    # Recommendations
    if active_count > 0:
        print("Active cameras detected on the following channels:")
        for result in results:
            if result['active']:
                print(f"  - Channel {result['channel']} ({result['frequency']} MHz)")
        print()
        print("Recommendations:")
        print("  1. Use channels with strongest signal (highest RSSI)")
        print("  2. Keep at least 40MHz spacing between channels")
        print("  3. Avoid channels with interference")
    else:
        print("No active signals detected.")
        print()
        print("Troubleshooting:")
        print("  1. Check camera units are powered on")
        print("  2. Verify RF receiver is connected properly")
        print("  3. Check antenna connections")
        print("  4. Try moving closer to cameras")
    
    print()
    print("Note: This is a simulated scanner for demonstration.")
    print("Lưu ý: Đây là máy quét mô phỏng để demo.")
    print("Real implementation requires RF receiver hardware.")
    print()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scan 5.8GHz RF channels / Quét kênh RF 5.8GHz'
    )
    parser.add_argument(
        '--duration', '-d',
        type=float,
        default=2.0,
        help='Scan duration per channel in seconds (default: 2.0)'
    )
    
    args = parser.parse_args()
    
    try:
        scan_channels(args.duration)
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user.")
        sys.exit(0)

if __name__ == '__main__':
    main()
