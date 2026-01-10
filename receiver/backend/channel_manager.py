"""
Channel Manager Module
Module quản lý kênh

Manages RF channel selection and automatic switching
Quản lý chọn kênh RF và chuyển đổi tự động

Author: Helmet Camera RF System
License: MIT
"""

import logging
import time

logger = logging.getLogger(__name__)

class ChannelManager:
    """Manages RF channel selection and scanning"""
    
    def __init__(self, config):
        """Initialize channel manager"""
        self.config = config
        self.channel_assignments = {}  # device_id -> channel
        self.channel_quality = {}  # channel -> RSSI
        self.last_scan_time = 0
    
    def set_channel(self, device_id, channel):
        """
        Assign a channel to a device
        
        Args:
            device_id: Device identifier
            channel: RF channel (1-8)
            
        Returns:
            bool: True if successful
        """
        if channel < 1 or channel > 8:
            logger.error(f"Invalid channel {channel}")
            return False
        
        self.channel_assignments[device_id] = channel
        logger.info(f"Assigned channel {channel} to {device_id}")
        return True
    
    def get_channel(self, device_id):
        """Get assigned channel for a device"""
        return self.channel_assignments.get(device_id)
    
    def scan_and_switch(self):
        """Scan channels and switch to best quality"""
        try:
            # Scan all channels for signal quality
            channels = self.config.get('receiver', {}).get('channels', [1, 2, 3, 4])
            
            for channel in channels:
                # In real implementation, measure actual RSSI
                # For now, simulate
                rssi = self._measure_channel_quality(channel)
                self.channel_quality[channel] = rssi
            
            # Find best channel
            if self.channel_quality:
                best_channel = max(self.channel_quality, key=self.channel_quality.get)
                best_rssi = self.channel_quality[best_channel]
                
                logger.debug(f"Best channel: {best_channel} (RSSI: {best_rssi} dBm)")
                
                return best_channel, best_rssi
            
        except Exception as e:
            logger.error(f"Error in scan_and_switch: {e}")
        
        return None, None
    
    def _measure_channel_quality(self, channel):
        """Measure signal quality for a channel"""
        # Simulate RSSI measurement
        # Real implementation would interface with RF receiver hardware
        return -90 + (channel * 5)  # dBm
    
    def get_channel_map(self):
        """Get current channel assignments"""
        return self.channel_assignments.copy()
    
    def get_channel_quality_map(self):
        """Get channel quality measurements"""
        return self.channel_quality.copy()
