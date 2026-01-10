#!/usr/bin/env python3
"""
Windows Performance Benchmark Tool
Công cụ đánh giá hiệu suất cho Windows

Benchmarks camera capture performance on Windows
Đánh giá hiệu suất chụp camera trên Windows

Author: Helmet Camera RF System
License: MIT
"""

import sys
import os
import platform
import time
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'receiver', 'backend'))


def print_header(text):
    """Print formatted header"""
    print()
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)
    print()


def print_section(text):
    """Print formatted section"""
    print()
    print(f"--- {text} ---")
    print()


def get_system_info():
    """Get system information"""
    info = {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
    }
    
    # Try to get CPU info
    try:
        import psutil
        info['cpu_count'] = psutil.cpu_count(logical=False)
        info['cpu_count_logical'] = psutil.cpu_count(logical=True)
        info['ram_total_gb'] = round(psutil.virtual_memory().total / (1024**3), 2)
    except ImportError:
        pass
    
    # Try to get GPU info
    try:
        import subprocess
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,driver_version,memory.total',
             '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            gpu_info = result.stdout.strip().split(',')
            if len(gpu_info) >= 3:
                info['gpu_name'] = gpu_info[0].strip()
                info['gpu_driver'] = gpu_info[1].strip()
                info['gpu_memory'] = gpu_info[2].strip()
    except:
        pass
    
    return info


def benchmark_camera(device_id, duration=10, resolution='640x480'):
    """
    Benchmark a camera
    
    Args:
        device_id: Camera device ID
        duration: Test duration in seconds
        resolution: Resolution to test (e.g., '640x480', '1920x1080')
    
    Returns:
        Dictionary with benchmark results
    """
    print(f"Benchmarking camera {device_id} at {resolution} for {duration} seconds...")
    
    try:
        from windows_camera_manager import WindowsCamera
    except ImportError:
        print("Error: windows_camera_manager not found")
        return None
    
    config = {
        'capture': {
            'resolution': resolution,
            'fps': 30,
            'format': 'MJPEG',
            'buffer_size': 1,
            'hardware_acceleration': True
        }
    }
    
    camera = WindowsCamera(device_id, config)
    
    if not camera.start():
        print(f"Failed to start camera {device_id}")
        return None
    
    # Wait for camera to stabilize
    time.sleep(1)
    
    # Collect stats
    start_time = time.time()
    frame_latencies = []
    
    while time.time() - start_time < duration:
        frame_data = camera.get_frame()
        if frame_data:
            stats = camera.get_stats()
            frame_latencies.append(stats.latency_ms)
        time.sleep(0.01)  # Small delay
    
    # Get final stats
    final_stats = camera.get_stats()
    camera.stop()
    
    # Calculate metrics
    if frame_latencies:
        avg_latency = sum(frame_latencies) / len(frame_latencies)
        min_latency = min(frame_latencies)
        max_latency = max(frame_latencies)
    else:
        avg_latency = min_latency = max_latency = 0
    
    results = {
        'device_id': device_id,
        'resolution': resolution,
        'duration': duration,
        'total_frames': final_stats.frame_count,
        'dropped_frames': final_stats.dropped_frames,
        'average_fps': final_stats.fps,
        'average_latency_ms': round(avg_latency, 2),
        'min_latency_ms': round(min_latency, 2),
        'max_latency_ms': round(max_latency, 2),
        'success': True
    }
    
    return results


def benchmark_multi_camera(num_cameras, duration=10):
    """
    Benchmark multiple cameras simultaneously
    
    Args:
        num_cameras: Number of cameras to test
        duration: Test duration in seconds
    
    Returns:
        List of benchmark results
    """
    print(f"Benchmarking {num_cameras} cameras simultaneously for {duration} seconds...")
    
    try:
        from windows_camera_manager import WindowsMultiCameraManager, WindowsPerformanceMonitor
    except ImportError:
        print("Error: windows_camera_manager not found")
        return []
    
    config = {
        'capture': {
            'resolution': '640x480',
            'fps': 30,
            'format': 'MJPEG',
            'buffer_size': 1,
            'hardware_acceleration': True
        },
        'performance': {
            'monitor_gpu': True,
            'log_stats': True,
            'stats_interval': 1
        }
    }
    
    manager = WindowsMultiCameraManager(config)
    monitor = WindowsPerformanceMonitor()
    
    # Discover cameras
    available = manager.discover_cameras()
    if len(available) < num_cameras:
        print(f"Only {len(available)} cameras available, testing with those")
        num_cameras = len(available)
    
    if num_cameras == 0:
        print("No cameras available")
        return []
    
    # Start cameras
    for i in range(num_cameras):
        manager.start_camera(available[i])
        time.sleep(0.5)  # Small delay between starts
    
    # Start monitoring
    monitor.start_monitoring(interval=1.0)
    
    # Wait for test duration
    start_time = time.time()
    time.sleep(duration)
    
    # Get stats
    camera_stats = manager.get_all_stats()
    system_stats = monitor.get_system_stats()
    
    # Stop monitoring and cameras
    monitor.stop_monitoring()
    manager.stop_all_cameras()
    
    # Compile results
    results = []
    for device_id, stats in camera_stats.items():
        results.append({
            'device_id': device_id,
            'total_frames': stats.frame_count,
            'dropped_frames': stats.dropped_frames,
            'average_fps': stats.fps,
            'average_latency_ms': stats.latency_ms,
        })
    
    results.append({
        'system_stats': {
            'cpu_percent': system_stats['cpu_percent'],
            'ram_percent': system_stats['ram_percent'],
            'gpu_stats': system_stats['gpu_stats']
        }
    })
    
    return results


def run_benchmarks():
    """Run all benchmarks"""
    print_header("Windows Camera Performance Benchmark")
    print_header("Đánh giá hiệu suất Camera Windows")
    
    # Check platform
    if platform.system() != 'Windows':
        print("Error: This benchmark is designed for Windows")
        return 1
    
    # System information
    print_section("System Information")
    sys_info = get_system_info()
    
    for key, value in sys_info.items():
        print(f"  {key:25s}: {value}")
    
    # Check dependencies
    print_section("Checking Dependencies")
    
    try:
        import cv2
        print(f"  ✓ OpenCV {cv2.__version__}")
    except ImportError:
        print("  ✗ OpenCV not installed")
        return 1
    
    try:
        import psutil
        print(f"  ✓ psutil {psutil.__version__}")
    except ImportError:
        print("  ⚠ psutil not installed (optional)")
    
    try:
        from windows_camera_manager import WindowsCamera, WindowsMultiCameraManager
        print("  ✓ windows_camera_manager available")
    except ImportError:
        print("  ✗ windows_camera_manager not found")
        return 1
    
    # Discover cameras
    print_section("Discovering Cameras")
    
    from windows_camera_manager import WindowsMultiCameraManager
    
    config = {'capture': {}}
    manager = WindowsMultiCameraManager(config)
    cameras = manager.discover_cameras()
    
    if not cameras:
        print("  No cameras found!")
        return 1
    
    print(f"  Found {len(cameras)} camera(s): {cameras}")
    
    # Benchmark each camera
    all_results = {
        'timestamp': datetime.now().isoformat(),
        'system_info': sys_info,
        'benchmarks': []
    }
    
    print_section("Single Camera Benchmarks")
    
    for camera_id in cameras[:3]:  # Test up to 3 cameras
        # Test at 480p
        result_480p = benchmark_camera(camera_id, duration=5, resolution='640x480')
        if result_480p:
            all_results['benchmarks'].append(result_480p)
            print(f"\nCamera {camera_id} @ 640x480:")
            print(f"  Average FPS: {result_480p['average_fps']:.1f}")
            print(f"  Average Latency: {result_480p['average_latency_ms']:.1f}ms")
            print(f"  Dropped Frames: {result_480p['dropped_frames']}")
        
        # Test at 1080p if supported
        result_1080p = benchmark_camera(camera_id, duration=5, resolution='1920x1080')
        if result_1080p:
            all_results['benchmarks'].append(result_1080p)
            print(f"\nCamera {camera_id} @ 1920x1080:")
            print(f"  Average FPS: {result_1080p['average_fps']:.1f}")
            print(f"  Average Latency: {result_1080p['average_latency_ms']:.1f}ms")
            print(f"  Dropped Frames: {result_1080p['dropped_frames']}")
    
    # Multi-camera benchmark
    if len(cameras) > 1:
        print_section("Multi-Camera Benchmark")
        
        multi_results = benchmark_multi_camera(len(cameras), duration=10)
        if multi_results:
            all_results['multi_camera'] = multi_results
            
            print(f"\n{len(cameras)} Cameras Simultaneously:")
            for result in multi_results[:-1]:  # Skip system stats
                print(f"  Camera {result['device_id']}:")
                print(f"    FPS: {result['average_fps']:.1f}")
                print(f"    Latency: {result['average_latency_ms']:.1f}ms")
                print(f"    Dropped: {result['dropped_frames']}")
            
            # System stats
            sys_stats = multi_results[-1]['system_stats']
            print(f"\n  System Resource Usage:")
            print(f"    CPU: {sys_stats['cpu_percent']:.1f}%")
            print(f"    RAM: {sys_stats['ram_percent']:.1f}%")
            if sys_stats['gpu_stats']:
                for gpu in sys_stats['gpu_stats']:
                    if 'utilization' in gpu:
                        print(f"    GPU ({gpu['name']}): {gpu['utilization']:.1f}%")
    
    # Save results
    print_section("Saving Results")
    
    output_dir = Path('benchmark_results')
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'benchmark_{timestamp}.json'
    
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"  Results saved to: {output_file}")
    
    # Summary
    print_section("Summary")
    
    print("  Benchmark completed successfully!")
    print(f"  Tested {len(cameras)} camera(s)")
    print(f"  Total benchmarks: {len(all_results['benchmarks'])}")
    
    print()
    print("  Recommendations:")
    
    # Analyze results and give recommendations
    if all_results['benchmarks']:
        avg_fps = sum(b['average_fps'] for b in all_results['benchmarks']) / len(all_results['benchmarks'])
        avg_latency = sum(b['average_latency_ms'] for b in all_results['benchmarks']) / len(all_results['benchmarks'])
        
        if avg_fps >= 28:
            print("    ✓ Frame rate is good (>28 FPS)")
        else:
            print("    ⚠ Frame rate is low, consider:")
            print("      - Lower resolution")
            print("      - Enable GPU acceleration")
            print("      - Close other applications")
        
        if avg_latency < 150:
            print("    ✓ Latency is excellent (<150ms)")
        elif avg_latency < 250:
            print("    ✓ Latency is acceptable (150-250ms)")
        else:
            print("    ⚠ Latency is high, consider:")
            print("      - Reduce buffer_size to 1")
            print("      - Use USB 3.0 ports")
            print("      - Better quality capture cards")
    
    print()
    return 0


if __name__ == '__main__':
    sys.exit(run_benchmarks())
