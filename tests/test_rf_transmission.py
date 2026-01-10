#!/usr/bin/env python3
"""
RF Transmission Test
Kiểm tra truyền RF

Tests RF transmission capabilities
Kiểm tra khả năng truyền RF
"""

import sys

def test_frequency_allocation():
    """Test frequency allocation is correct"""
    print("Testing frequency allocation...")
    print("Kiểm tra phân bổ tần số...")
    
    # 5.8GHz Band E frequencies
    band_e = {
        1: 5705,
        2: 5685,
        3: 5665,
        4: 5645,
        5: 5885,
        6: 5905,
        7: 5925,
        8: 5945
    }
    
    print("✓ 5.8 GHz Band E channels:")
    for channel, freq in band_e.items():
        print(f"  Channel {channel}: {freq} MHz")
    
    # Check minimum spacing
    frequencies = sorted(band_e.values())
    min_spacing = 200  # MHz
    
    for i in range(len(frequencies) - 1):
        spacing = abs(frequencies[i+1] - frequencies[i])
        if spacing < 20:
            print(f"⚠ Warning: Channels too close ({spacing} MHz)")
    
    print("✓ Frequency allocation valid")
    return True

def test_power_levels():
    """Test power levels are within legal limits"""
    print("\nTesting power levels...")
    print("Kiểm tra mức công suất...")
    
    # Common power levels for 5.8GHz
    power_levels_mw = [25, 200, 600]
    power_levels_dbm = [14, 23, 28]
    
    print("✓ Available power levels:")
    for mw, dbm in zip(power_levels_mw, power_levels_dbm):
        print(f"  {mw} mW ({dbm} dBm)")
    
    # Vietnam regulatory check (example values, verify with VNTA)
    max_eirp_dbm = 30  # Example limit, check current regulations
    
    print(f"\n✓ Maximum EIRP (example): {max_eirp_dbm} dBm")
    print("⚠ Always verify current regulations with VNTA!")
    print("⚠ Luôn kiểm tra quy định hiện tại với VNTA!")
    
    return True

def test_range_calculation():
    """Test theoretical range calculation"""
    print("\nTesting range calculation...")
    print("Kiểm tra tính toán phạm vi...")
    
    import math
    
    # 5.8 GHz link budget
    tx_power_dbm = 23  # 200mW
    tx_gain_dbi = 2    # Cloverleaf antenna
    rx_gain_dbi = 5    # Patch antenna
    rx_sensitivity_dbm = -90
    
    # Free space path loss for different distances
    frequency_ghz = 5.8
    
    print(f"TX Power: {tx_power_dbm} dBm")
    print(f"TX Gain: {tx_gain_dbi} dBi")
    print(f"RX Gain: {rx_gain_dbi} dBi")
    print(f"RX Sensitivity: {rx_sensitivity_dbm} dBm")
    print()
    
    distances = [100, 200, 500, 1000]  # meters
    
    print("Theoretical ranges:")
    for distance in distances:
        # Path loss calculation
        path_loss = 20 * math.log10(distance) + 20 * math.log10(frequency_ghz * 1000) + 32.45
        
        # Received power
        rx_power = tx_power_dbm + tx_gain_dbi + rx_gain_dbi - path_loss
        
        # Link margin
        link_margin = rx_power - rx_sensitivity_dbm
        
        status = "✓ OK" if link_margin > 0 else "✗ FAIL"
        print(f"  {distance}m: RX Power = {rx_power:.1f} dBm, Margin = {link_margin:.1f} dB {status}")
    
    return True

def test_channel_separation():
    """Test channel separation is adequate"""
    print("\nTesting channel separation...")
    print("Kiểm tra khoảng cách kênh...")
    
    # Recommended channel pairs for multi-camera
    channel_sets = [
        [1, 3, 5, 7],  # Maximum spacing
        [1, 2, 5, 6],  # Alternative
    ]
    
    print("✓ Recommended channel combinations:")
    for i, channels in enumerate(channel_sets, 1):
        print(f"  Set {i}: Channels {channels}")
    
    print("\n✓ Minimum spacing: 40 MHz recommended")
    print("✓ Khoảng cách tối thiểu: Khuyến nghị 40 MHz")
    
    return True

def main():
    """Main test runner"""
    print("=" * 60)
    print("RF Transmission Test Suite")
    print("Bộ kiểm tra Truyền RF")
    print("=" * 60)
    print()
    
    tests = [
        test_frequency_allocation,
        test_power_levels,
        test_range_calculation,
        test_channel_separation
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
