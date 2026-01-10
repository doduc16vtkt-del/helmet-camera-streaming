"""
Telemetry Receiver Module
Module thu telemetry

Receives telemetry data from helmet cameras via 2.4GHz RF
Thu dữ liệu telemetry từ camera mũ bảo hiểm qua RF 2.4GHz

Author: Helmet Camera RF System
License: MIT
"""

import logging
import time
import threading
try:
    from RF24 import RF24, RF24_PA_MAX, RF24_250KBPS
    RF24_AVAILABLE = True
except ImportError:
    RF24_AVAILABLE = False
    logging.warning("RF24 library not available, telemetry will be simulated")

logger = logging.getLogger(__name__)

class TelemetryReceiver:
    """Receives telemetry data via nRF24L01+"""
    
    def __init__(self, config):
        """Initialize telemetry receiver"""
        self.config = config
        self.radio = None
        self.initialized = False
        self.receiving = False
        self.last_data = {}
    
    def initialize(self):
        """Initialize nRF24L01+ receiver"""
        if not RF24_AVAILABLE:
            logger.warning("RF24 not available, using simulated mode")
            self.initialized = True
            return True
        
        try:
            telemetry_config = self.config.get('rf_telemetry', {})
            
            if not telemetry_config.get('enabled', False):
                logger.info("Telemetry receiver disabled in config")
                return False
            
            # Initialize radio
            pins = telemetry_config.get('pins', {})
            ce_pin = pins.get('ce', 22)
            csn_pin = pins.get('csn', 0)
            
            self.radio = RF24(ce_pin, csn_pin, 8000000)
            
            if not self.radio.begin():
                logger.error("nRF24L01+ initialization failed")
                return False
            
            # Configure radio
            channel = telemetry_config.get('channel', 76)
            self.radio.setPALevel(RF24_PA_MAX)
            self.radio.setDataRate(RF24_250KBPS)
            self.radio.setChannel(channel)
            self.radio.enableDynamicPayloads()
            self.radio.setAutoAck(True)
            
            # Open reading pipe (address from config or default)
            address_str = telemetry_config.get('address', 'HLMT1')
            address = address_str.encode('utf-8')[:5]  # Max 5 bytes for nRF24
            self.radio.openReadingPipe(1, address)
            self.radio.startListening()
            
            self.initialized = True
            logger.info(f"Telemetry receiver initialized on channel {channel}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize telemetry receiver: {e}")
            return False
    
    def receive(self):
        """
        Receive telemetry data
        
        Returns:
            dict: Telemetry data, or None if no data available
        """
        if not self.initialized:
            return None
        
        if not RF24_AVAILABLE:
            # Return simulated data
            return self._get_simulated_data()
        
        try:
            if self.radio.available():
                # Read payload
                payload_size = self.radio.getDynamicPayloadSize()
                payload = self.radio.read(payload_size)
                
                # Parse payload
                data = self._parse_payload(payload)
                
                if data:
                    self.last_data = data
                    return data
            
        except Exception as e:
            logger.error(f"Error receiving telemetry: {e}")
        
        return None
    
    def _parse_payload(self, payload):
        """Parse received payload into telemetry data"""
        try:
            # Convert bytes to string
            message = payload.decode('utf-8')
            
            # Simple text protocol parser
            if message.startswith('TELEM:'):
                parts = message.split(':')
                if len(parts) >= 6:
                    return {
                        'device_id': parts[1],
                        'battery_voltage': float(parts[2]),
                        'battery_percent': int(parts[3]),
                        'temperature': float(parts[4]),
                        'uptime': float(parts[5]),
                        'timestamp': time.time()
                    }
            elif message.startswith('INFO:'):
                parts = message.split(':')
                if len(parts) >= 3:
                    logger.info(f"Device info: {parts[1]} v{parts[2]}")
            elif message.startswith('ALERT:'):
                parts = message.split(':')
                if len(parts) >= 2:
                    logger.warning(f"Alert received: code {parts[1]}")
            
        except Exception as e:
            logger.error(f"Failed to parse payload: {e}")
        
        return None
    
    def _get_simulated_data(self):
        """Get simulated telemetry data for testing"""
        return {
            'device_id': 'HELMET_SIM_01',
            'battery_voltage': 11.5,
            'battery_percent': 75,
            'temperature': 45.2,
            'uptime': time.time() % 1000,
            'timestamp': time.time(),
            'rssi': -75
        }
    
    def close(self):
        """Close telemetry receiver"""
        if self.radio and RF24_AVAILABLE:
            self.radio.stopListening()
            logger.info("Telemetry receiver closed")
