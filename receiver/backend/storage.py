"""
Storage Manager Module
Module quản lý lưu trữ

Manages video recording and storage
Quản lý ghi video và lưu trữ

Author: Helmet Camera RF System
License: MIT
"""

import logging
import os
import cv2
import time
from datetime import datetime, timedelta
import threading
import glob

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages video recording and storage"""
    
    def __init__(self, config):
        """Initialize storage manager"""
        self.config = config
        self.recording_config = config.get('recording', {})
        self.active_recordings = {}  # device_id -> VideoWriter
        self.recording_threads = {}
        self.recording_paths = {}
        
        # Create recording directory
        self.base_path = self.recording_config.get('path', './recordings')
        os.makedirs(self.base_path, exist_ok=True)
    
    def start_recording(self, device_id, video_capture=None):
        """
        Start recording video from a device
        
        Args:
            device_id: Device identifier
            video_capture: VideoCapture instance
            
        Returns:
            bool: True if successful
        """
        if device_id in self.active_recordings:
            logger.warning(f"Already recording {device_id}")
            return True
        
        try:
            # Generate filename
            filename = self._generate_filename(device_id)
            filepath = os.path.join(self.base_path, filename)
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'H264', 'XVID'
            fps = 30
            frame_size = (640, 480)
            
            writer = cv2.VideoWriter(filepath, fourcc, fps, frame_size)
            
            if not writer.isOpened():
                logger.error(f"Failed to create video writer for {filepath}")
                return False
            
            self.active_recordings[device_id] = writer
            self.recording_paths[device_id] = filepath
            
            logger.info(f"Started recording {device_id} to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self, device_id):
        """
        Stop recording video
        
        Args:
            device_id: Device identifier
            
        Returns:
            bool: True if successful
        """
        if device_id not in self.active_recordings:
            logger.warning(f"Not recording {device_id}")
            return False
        
        try:
            # Release video writer
            writer = self.active_recordings[device_id]
            writer.release()
            
            filepath = self.recording_paths.get(device_id, 'unknown')
            del self.active_recordings[device_id]
            del self.recording_paths[device_id]
            
            logger.info(f"Stopped recording {device_id}, saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return False
    
    def write_frame(self, device_id, frame):
        """
        Write a frame to recording
        
        Args:
            device_id: Device identifier
            frame: Video frame (numpy array)
        """
        if device_id in self.active_recordings:
            try:
                self.active_recordings[device_id].write(frame)
            except Exception as e:
                logger.error(f"Failed to write frame: {e}")
    
    def is_recording(self, device_id):
        """Check if device is currently recording"""
        return device_id in self.active_recordings
    
    def list_recordings(self):
        """
        List all recordings
        
        Returns:
            list: List of recording information
        """
        recordings = []
        
        try:
            pattern = os.path.join(self.base_path, '*.mp4')
            files = glob.glob(pattern)
            
            for filepath in files:
                stat = os.stat(filepath)
                recordings.append({
                    'filename': os.path.basename(filepath),
                    'path': filepath,
                    'size': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime
                })
            
            # Sort by creation time (newest first)
            recordings.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list recordings: {e}")
        
        return recordings
    
    def cleanup_old_recordings(self):
        """Delete old recordings based on retention policy"""
        try:
            retention_days = self.recording_config.get('retention_days', 7)
            cutoff_time = time.time() - (retention_days * 24 * 3600)
            
            recordings = self.list_recordings()
            deleted_count = 0
            
            for recording in recordings:
                if recording['created'] < cutoff_time:
                    try:
                        os.remove(recording['path'])
                        deleted_count += 1
                        logger.info(f"Deleted old recording: {recording['filename']}")
                    except Exception as e:
                        logger.error(f"Failed to delete {recording['filename']}: {e}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old recording(s)")
            
        except Exception as e:
            logger.error(f"Failed to cleanup recordings: {e}")
    
    def _generate_filename(self, device_id):
        """Generate filename for recording"""
        pattern = self.recording_config.get('filename_pattern', '{device_id}_{timestamp}')
        timestamp_format = self.recording_config.get('timestamp_format', '%Y%m%d_%H%M%S')
        
        timestamp = datetime.now().strftime(timestamp_format)
        filename = pattern.format(device_id=device_id, timestamp=timestamp)
        
        return f"{filename}.mp4"
    
    def get_disk_usage(self):
        """Get disk usage statistics"""
        try:
            stat = os.statvfs(self.base_path)
            
            # Calculate sizes in GB
            total = (stat.f_blocks * stat.f_frsize) / (1024**3)
            free = (stat.f_bavail * stat.f_frsize) / (1024**3)
            used = total - free
            used_percent = (used / total) * 100 if total > 0 else 0
            
            return {
                'total_gb': round(total, 2),
                'used_gb': round(used, 2),
                'free_gb': round(free, 2),
                'used_percent': round(used_percent, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get disk usage: {e}")
            return None
