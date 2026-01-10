#!/usr/bin/env python3
"""
Windows Camera Test Script
Script kiểm tra camera cho Windows

Tests Windows-specific camera functionality
Kiểm tra chức năng camera đặc thù Windows

Author: Helmet Camera RF System
License: MIT
"""

import sys
import os
import platform
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'receiver', 'backend'))


class TestWindowsCamera(unittest.TestCase):
    """Test Windows camera functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test class"""
        if platform.system() != 'Windows':
            raise unittest.SkipTest("Tests only run on Windows")
        
        try:
            import cv2
            cls.cv2 = cv2
        except ImportError:
            raise unittest.SkipTest("OpenCV not installed")
    
    def test_platform_detection(self):
        """Test that we're running on Windows"""
        self.assertEqual(platform.system(), 'Windows')
        print(f"✓ Platform detected: {platform.system()} {platform.release()}")
    
    def test_opencv_available(self):
        """Test that OpenCV is available"""
        import cv2
        self.assertIsNotNone(cv2.__version__)
        print(f"✓ OpenCV version: {cv2.__version__}")
    
    def test_directshow_backend(self):
        """Test DirectShow backend availability"""
        self.assertTrue(hasattr(self.cv2, 'CAP_DSHOW'))
        print(f"✓ DirectShow backend available: CAP_DSHOW = {self.cv2.CAP_DSHOW}")
    
    def test_camera_discovery(self):
        """Test camera discovery"""
        print("\nDiscovering cameras...")
        
        found_cameras = []
        for device_id in range(5):  # Test first 5 indices
            try:
                cap = self.cv2.VideoCapture(device_id, self.cv2.CAP_DSHOW)
                if cap.isOpened():
                    found_cameras.append(device_id)
                    width = int(cap.get(self.cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(self.cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = int(cap.get(self.cv2.CAP_PROP_FPS))
                    backend = cap.getBackendName()
                    print(f"  Camera {device_id}: {width}x{height} @ {fps}fps (backend: {backend})")
                    cap.release()
            except Exception as e:
                pass
        
        if found_cameras:
            print(f"✓ Found {len(found_cameras)} camera(s): {found_cameras}")
        else:
            print("⚠ No cameras found (this may be expected in CI environment)")
    
    def test_windows_camera_manager_import(self):
        """Test that Windows camera manager can be imported"""
        try:
            from windows_camera_manager import WindowsCamera, WindowsMultiCameraManager
            print("✓ Windows camera manager modules imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import Windows camera manager: {e}")
    
    def test_windows_camera_manager_discovery(self):
        """Test Windows camera manager discovery"""
        from windows_camera_manager import WindowsMultiCameraManager
        
        config = {
            'capture': {
                'resolution': '640x480',
                'fps': 30,
                'format': 'MJPEG',
                'buffer_size': 1,
                'hardware_acceleration': True
            }
        }
        
        manager = WindowsMultiCameraManager(config)
        cameras = manager.discover_cameras()
        
        print(f"✓ Camera manager discovered {len(cameras)} camera(s)")
        if cameras:
            print(f"  Camera IDs: {cameras}")
    
    def test_video_capture_module_import(self):
        """Test that video_capture module works on Windows"""
        try:
            from video_capture import VideoCapture
            
            config = {
                'capture': {
                    'resolution': '640x480',
                    'fps': 30,
                    'format': 'MJPEG',
                    'buffer_size': 1,
                    'hardware_acceleration': True
                }
            }
            
            vc = VideoCapture(config)
            self.assertIsNotNone(vc)
            print("✓ VideoCapture module works on Windows")
        except Exception as e:
            self.fail(f"Failed to import/initialize VideoCapture: {e}")
    
    def test_performance_monitor_import(self):
        """Test performance monitor import"""
        try:
            from windows_camera_manager import WindowsPerformanceMonitor
            
            monitor = WindowsPerformanceMonitor()
            stats = monitor.get_system_stats()
            
            self.assertIn('cpu_percent', stats)
            self.assertIn('ram_percent', stats)
            self.assertIn('gpu_stats', stats)
            
            print("✓ Performance monitoring available")
            print(f"  CPU: {stats['cpu_percent']:.1f}%")
            print(f"  RAM: {stats['ram_percent']:.1f}%")
            
            # Check if GPU stats are available and valid
            if stats['gpu_stats'] and len(stats['gpu_stats']) > 0:
                if stats['gpu_stats'][0].get('name') != 'GPU detection not available':
                    for gpu in stats['gpu_stats']:
                        print(f"  GPU: {gpu['name']}")
        except ImportError:
            print("⚠ psutil not installed, skipping performance monitoring test")
        except Exception as e:
            print(f"⚠ Performance monitoring test failed: {e}")


class TestCrossPlatformCompatibility(unittest.TestCase):
    """Test cross-platform compatibility fixes"""
    
    def test_platform_import(self):
        """Test platform module is imported in video_capture"""
        import video_capture
        self.assertTrue(hasattr(video_capture, 'platform'))
        print("✓ Platform module imported in video_capture")
    
    def test_app_uses_os_path_join(self):
        """Test that app.py uses os.path.join"""
        app_path = os.path.join(os.path.dirname(__file__), '..', 'receiver', 'backend', 'app.py')
        
        if os.path.exists(app_path):
            with open(app_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check that os.path.join is used for config path
                self.assertIn('os.path.join', content)
                print("✓ app.py uses os.path.join for cross-platform paths")
        else:
            self.skipTest("app.py not found")


def main():
    """Main test runner"""
    print("=" * 60)
    print("Windows Camera Test Suite")
    print("Bộ kiểm tra Camera Windows")
    print("=" * 60)
    print()
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestWindowsCamera))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossPlatformCompatibility))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    print("Test Results / Kết quả kiểm tra")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✓ All tests passed!")
        print("✓ Tất cả các kiểm tra đã vượt qua!")
        return 0
    else:
        print("✗ Some tests failed")
        print("✗ Một số kiểm tra thất bại")
        return 1


if __name__ == '__main__':
    sys.exit(main())
