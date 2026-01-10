#!/usr/bin/env python3
"""
Windows MSMF Camera Test Utility
Công cụ kiểm tra Camera MSMF cho Windows

Comprehensive testing utility for MSMF backend camera compatibility
Công cụ kiểm tra toàn diện cho khả năng tương thích camera backend MSMF

Author: Helmet Camera RF System
License: MIT
"""

import sys
import cv2
import time
import platform
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_camera_backend(device_id, backend_name, backend_flag):
    """
    Test camera with specific backend
    
    Args:
        device_id: Camera device index
        backend_name: Backend name for display
        backend_flag: OpenCV backend flag
        
    Returns:
        dict: Test results
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing Camera {device_id} with {backend_name} backend")
    logger.info(f"{'='*60}")
    
    result = {
        'device_id': device_id,
        'backend': backend_name,
        'success': False,
        'error': None,
        'can_open': False,
        'can_read_before_config': False,
        'can_read_after_config': False,
        'properties': {}
    }
    
    try:
        # Step 1: Try to open camera
        logger.info(f"Step 1: Opening camera with {backend_name}...")
        cap = cv2.VideoCapture(device_id, backend_flag)
        
        if not cap.isOpened():
            result['error'] = "Failed to open camera"
            logger.error(f"❌ Failed to open camera {device_id}")
            return result
        
        result['can_open'] = True
        logger.info(f"✅ Camera {device_id} opened successfully")
        
        # Step 2: Try reading frame BEFORE setting properties
        logger.info("Step 2: Reading initial frame (before setting properties)...")
        ret, frame = cap.read()
        
        if not ret:
            result['error'] = "Failed to read initial frame"
            logger.error("❌ Failed to read initial frame")
            cap.release()
            return result
        
        result['can_read_before_config'] = True
        logger.info(f"✅ Initial frame captured: {frame.shape}")
        
        # Step 3: Try setting properties
        logger.info("Step 3: Setting camera properties...")
        try:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            logger.info("✅ Properties set successfully")
        except Exception as e:
            logger.warning(f"⚠ Could not set all properties: {e}")
        
        # Step 4: Try reading frame AFTER setting properties
        logger.info("Step 4: Reading frame after setting properties...")
        ret, frame = cap.read()
        
        if not ret:
            result['error'] = "Failed to read frame after setting properties"
            logger.error("❌ Failed to read frame after setting properties")
            cap.release()
            return result
        
        result['can_read_after_config'] = True
        logger.info(f"✅ Frame captured after config: {frame.shape}")
        
        # Step 5: Get actual properties
        logger.info("Step 5: Reading actual camera properties...")
        result['properties'] = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'backend': cap.getBackendName() if hasattr(cap, 'getBackendName') else 'Unknown'
        }
        
        logger.info(f"Actual settings:")
        logger.info(f"  Resolution: {result['properties']['width']}x{result['properties']['height']}")
        logger.info(f"  FPS: {result['properties']['fps']}")
        logger.info(f"  Backend: {result['properties']['backend']}")
        
        # Step 6: Capture test (3 seconds)
        logger.info("Step 6: Testing continuous capture (3 seconds)...")
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 3.0:
            ret, frame = cap.read()
            if ret:
                frame_count += 1
            else:
                logger.warning("Frame read failed during capture test")
                break
        
        elapsed = time.time() - start_time
        actual_fps = frame_count / elapsed if elapsed > 0 else 0
        
        logger.info(f"✅ Captured {frame_count} frames in {elapsed:.2f}s ({actual_fps:.1f} fps)")
        result['properties']['measured_fps'] = actual_fps
        
        cap.release()
        result['success'] = True
        logger.info(f"✅ All tests passed for {backend_name}!")
        
    except Exception as e:
        result['error'] = str(e)
        logger.error(f"❌ Error testing camera: {e}")
        
    return result


def test_without_initial_read(device_id, backend_flag):
    """
    Test setting properties WITHOUT reading initial frame first
    This should fail with MSMF backend
    
    Args:
        device_id: Camera device index
        backend_flag: OpenCV backend flag
        
    Returns:
        bool: True if test passes (properties can be set), False otherwise
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing Property Setting WITHOUT Initial Frame Read")
    logger.info(f"{'='*60}")
    
    try:
        cap = cv2.VideoCapture(device_id, backend_flag)
        
        if not cap.isOpened():
            logger.error("❌ Failed to open camera")
            return False
        
        logger.info("Attempting to set properties immediately (no initial read)...")
        
        # Try setting properties WITHOUT reading initial frame
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Now try to read frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            logger.error("❌ Failed to read frame after setting properties (expected with MSMF)")
            return False
        else:
            logger.info("✅ Frame read successful (unexpected - this backend may not require initial read)")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("Windows Camera MSMF Backend Test Utility")
    print("Công cụ Kiểm tra Backend MSMF Camera Windows")
    print("="*60)
    print()
    
    # Check platform
    if platform.system() != 'Windows':
        logger.error("❌ This test is designed for Windows only")
        logger.error("Current platform: " + platform.system())
        return 1
    
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"OpenCV: {cv2.__version__}")
    print()
    
    # Check available backends
    logger.info("Available backends:")
    backends = [
        ('MSMF', cv2.CAP_MSMF if hasattr(cv2, 'CAP_MSMF') else None),
        ('DSHOW', cv2.CAP_DSHOW if hasattr(cv2, 'CAP_DSHOW') else None),
    ]
    
    for name, flag in backends:
        if flag is not None:
            logger.info(f"  ✅ {name} (flag: {flag})")
        else:
            logger.info(f"  ❌ {name} not available")
    
    print()
    
    # Discover cameras with MSMF
    logger.info("Discovering cameras with MSMF backend...")
    available_cameras = []
    
    for i in range(10):
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_MSMF)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(i)
                    logger.info(f"  ✅ Camera {i} found")
                cap.release()
            else:
                break
        except Exception as e:
            logger.debug(f"No camera at index {i}")
            break
    
    if not available_cameras:
        logger.error("❌ No cameras found!")
        logger.error("Please connect a camera and try again.")
        return 1
    
    logger.info(f"\nFound {len(available_cameras)} camera(s): {available_cameras}")
    print()
    
    # Test each camera
    all_results = []
    
    for device_id in available_cameras:
        # Test with MSMF (recommended)
        result_msmf = test_camera_backend(device_id, "MSMF", cv2.CAP_MSMF)
        all_results.append(result_msmf)
        
        # Test with DSHOW (old method) for comparison
        if hasattr(cv2, 'CAP_DSHOW'):
            result_dshow = test_camera_backend(device_id, "DSHOW", cv2.CAP_DSHOW)
            all_results.append(result_dshow)
        
        # Test without initial read (should fail with MSMF)
        test_without_initial_read(device_id, cv2.CAP_MSMF)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary / Tóm tắt Kiểm tra")
    print("="*60)
    
    for result in all_results:
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"\nCamera {result['device_id']} - {result['backend']}: {status}")
        
        if result['success']:
            props = result['properties']
            print(f"  Resolution: {props['width']}x{props['height']}")
            print(f"  FPS (reported): {props['fps']:.1f}")
            print(f"  FPS (measured): {props.get('measured_fps', 0):.1f}")
            print(f"  Backend: {props['backend']}")
        else:
            print(f"  Error: {result['error']}")
    
    # Recommendations
    print("\n" + "="*60)
    print("Recommendations / Khuyến nghị")
    print("="*60)
    
    msmf_works = any(r['success'] and r['backend'] == 'MSMF' for r in all_results)
    
    if msmf_works:
        print("\n✅ MSMF backend is working correctly!")
        print("✅ Backend MSMF hoạt động chính xác!")
        print("\nYour configuration is correct:")
        print("  1. Camera opens with MSMF")
        print("  2. Initial frame read works")
        print("  3. Properties can be set after initial read")
        print("  4. Continuous capture works")
        print("\n🎉 Your system is ready for production use!")
    else:
        print("\n❌ MSMF backend has issues")
        print("❌ Backend MSMF có vấn đề")
        print("\nTroubleshooting steps:")
        print("  1. Update Windows to latest version")
        print("  2. Update camera drivers")
        print("  3. Try different USB port")
        print("  4. Update OpenCV: pip install --upgrade opencv-python")
        print("  5. Check Windows Camera app works with camera")
    
    print()
    return 0 if msmf_works else 1


if __name__ == '__main__':
    sys.exit(main())
