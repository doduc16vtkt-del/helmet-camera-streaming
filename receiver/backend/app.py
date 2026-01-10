"""
Central Receiver Station - Backend API
Trạm tiếp nhận trung tâm - API Backend

Flask-based web server for receiving and managing RF camera feeds
Web server dựa trên Flask để nhận và quản lý luồng camera RF

Author: Helmet Camera RF System
License: MIT
"""

from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import yaml
import logging
import threading
import time
from datetime import datetime
import os
import platform

from rf_receiver import RFReceiver
from video_capture import VideoCapture
from channel_manager import ChannelManager
from telemetry_receiver import TelemetryReceiver
from storage import StorageManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/receiver.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')
# Use environment variable or generate random secret key for production security
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load configuration
def load_config():
    """Load configuration from YAML file"""
    # Use os.path.join for cross-platform compatibility
    config_path = os.path.join('..', '..', 'configs', 'receiver_config.yaml')
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return get_default_config()

def get_default_config():
    """Get default configuration"""
    return {
        'receiver': {
            'channels': list(range(1, 9)),
            'scan_interval': 1000,
            'auto_switch': True
        },
        'dashboard': {
            'host': '0.0.0.0',
            'port': 8080,
            'max_cameras': 8
        },
        'recording': {
            'enabled': True,
            'path': './recordings',
            'format': 'mp4'
        }
    }

config = load_config()

# Initialize system components
logger.info(f"Platform: {platform.system()}")
if platform.system() == 'Windows':
    logger.info("Using Media Foundation (MSMF) backend for cameras")

rf_receiver = RFReceiver(config)
video_capture = VideoCapture(config)
channel_manager = ChannelManager(config)
telemetry_receiver = TelemetryReceiver(config)
storage_manager = StorageManager(config)

# Global state
system_state = {
    'active_cameras': {},
    'current_channels': {},
    'recording_status': {},
    'telemetry_data': {},
    'system_uptime': time.time()
}

# ============================================
# Web Routes / Các route web
# ============================================

@app.route('/')
def index():
    """Serve main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'online',
        'uptime': time.time() - system_state['system_uptime'],
        'active_cameras': len(system_state['active_cameras']),
        'recording': len(system_state['recording_status'])
    })

@app.route('/api/cameras')
def get_cameras():
    """Get list of active cameras"""
    cameras = []
    for device_id, camera_data in system_state['active_cameras'].items():
        cameras.append({
            'device_id': device_id,
            'channel': camera_data.get('channel'),
            'signal_strength': camera_data.get('rssi', 0),
            'battery': camera_data.get('battery_percent', 0),
            'recording': system_state['recording_status'].get(device_id, False),
            'last_seen': camera_data.get('last_seen', 0)
        })
    return jsonify({'cameras': cameras})

@app.route('/api/telemetry/<device_id>')
def get_telemetry(device_id):
    """Get telemetry data for specific camera"""
    if device_id in system_state['telemetry_data']:
        return jsonify(system_state['telemetry_data'][device_id])
    return jsonify({'error': 'Camera not found'}), 404

@app.route('/api/recording/start/<device_id>', methods=['POST'])
def start_recording(device_id):
    """Start recording for a camera"""
    try:
        if storage_manager.start_recording(device_id):
            system_state['recording_status'][device_id] = True
            socketio.emit('recording_started', {'device_id': device_id})
            return jsonify({'success': True, 'device_id': device_id})
        return jsonify({'success': False, 'error': 'Failed to start recording'}), 500
    except Exception as e:
        logger.error(f"Failed to start recording: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recording/stop/<device_id>', methods=['POST'])
def stop_recording(device_id):
    """Stop recording for a camera"""
    try:
        if storage_manager.stop_recording(device_id):
            system_state['recording_status'][device_id] = False
            socketio.emit('recording_stopped', {'device_id': device_id})
            return jsonify({'success': True, 'device_id': device_id})
        return jsonify({'success': False, 'error': 'Failed to stop recording'}), 500
    except Exception as e:
        logger.error(f"Failed to stop recording: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/channel/set/<device_id>/<int:channel>', methods=['POST'])
def set_channel(device_id, channel):
    """Set RF channel for a camera"""
    try:
        if channel_manager.set_channel(device_id, channel):
            return jsonify({'success': True, 'device_id': device_id, 'channel': channel})
        return jsonify({'success': False, 'error': 'Invalid channel'}), 400
    except Exception as e:
        logger.error(f"Failed to set channel: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recordings')
def list_recordings():
    """List all recordings"""
    try:
        recordings = storage_manager.list_recordings()
        return jsonify({'recordings': recordings})
    except Exception as e:
        logger.error(f"Failed to list recordings: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# WebSocket Events / Sự kiện WebSocket
# ============================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('system_status', {
        'status': 'connected',
        'cameras': list(system_state['active_cameras'].keys())
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('request_video_frame')
def handle_video_request(data):
    """Handle video frame request"""
    device_id = data.get('device_id')
    # Send video frame via WebSocket
    # Implementation would stream actual video frames
    pass

# ============================================
# Background Tasks / Tác vụ nền
# ============================================

def telemetry_listener_task():
    """Background task to listen for telemetry data"""
    logger.info("Starting telemetry listener task")
    
    while True:
        try:
            # Receive telemetry data
            telemetry_data = telemetry_receiver.receive()
            
            if telemetry_data:
                device_id = telemetry_data.get('device_id')
                
                # Update system state
                system_state['telemetry_data'][device_id] = telemetry_data
                system_state['active_cameras'][device_id] = {
                    'channel': telemetry_data.get('channel', 1),
                    'rssi': telemetry_data.get('rssi', 0),
                    'battery_percent': telemetry_data.get('battery_percent', 0),
                    'last_seen': time.time()
                }
                
                # Emit to connected clients
                socketio.emit('telemetry_update', {
                    'device_id': device_id,
                    'data': telemetry_data
                })
                
                logger.debug(f"Telemetry received from {device_id}")
                
        except Exception as e:
            logger.error(f"Error in telemetry listener: {e}")
        
        time.sleep(0.1)  # Small delay to prevent busy loop

def channel_scanner_task():
    """Background task to scan RF channels"""
    logger.info("Starting channel scanner task")
    
    while True:
        try:
            if config['receiver'].get('auto_switch', False):
                # Scan channels and switch to strongest signal
                channel_manager.scan_and_switch()
        except Exception as e:
            logger.error(f"Error in channel scanner: {e}")
        
        time.sleep(config['receiver'].get('scan_interval', 1000) / 1000.0)

def camera_monitor_task():
    """Monitor camera connections and clean up stale entries"""
    logger.info("Starting camera monitor task")
    
    while True:
        try:
            current_time = time.time()
            stale_timeout = 10  # seconds
            
            # Check for stale cameras
            stale_cameras = []
            for device_id, camera_data in system_state['active_cameras'].items():
                if current_time - camera_data.get('last_seen', 0) > stale_timeout:
                    stale_cameras.append(device_id)
            
            # Remove stale cameras
            for device_id in stale_cameras:
                logger.warning(f"Camera {device_id} connection lost")
                del system_state['active_cameras'][device_id]
                socketio.emit('camera_disconnected', {'device_id': device_id})
                
        except Exception as e:
            logger.error(f"Error in camera monitor: {e}")
        
        time.sleep(5)

# ============================================
# Initialization / Khởi tạo
# ============================================

def initialize_system():
    """Initialize all system components"""
    logger.info("=" * 60)
    logger.info("Helmet Camera RF Receiver Station Starting")
    logger.info("Trạm Tiếp Nhận Camera Mũ Bảo Hiểm RF")
    logger.info("=" * 60)
    
    # Create necessary directories (cross-platform)
    os.makedirs('logs', exist_ok=True)
    os.makedirs(config['recording']['path'], exist_ok=True)
    
    # Initialize components
    if not rf_receiver.initialize():
        logger.error("Failed to initialize RF receiver")
    
    if not telemetry_receiver.initialize():
        logger.error("Failed to initialize telemetry receiver")
    
    # Start background tasks
    threading.Thread(target=telemetry_listener_task, daemon=True).start()
    threading.Thread(target=channel_scanner_task, daemon=True).start()
    threading.Thread(target=camera_monitor_task, daemon=True).start()
    
    logger.info("System initialized successfully")
    logger.info(f"Dashboard available at http://0.0.0.0:{config['dashboard']['port']}")
    
    # Auto-launch browser on Windows if configured
    if platform.system() == 'Windows' and config.get('dashboard', {}).get('open_browser', False):
        import webbrowser
        port = config['dashboard']['port']
        url = f"http://localhost:{port}"
        logger.info(f"Auto-launching browser at {url}")
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()

# ============================================
# Main Entry Point / Điểm vào chính
# ============================================

if __name__ == '__main__':
    initialize_system()
    
    # Run Flask-SocketIO server
    socketio.run(
        app,
        host=config['dashboard']['host'],
        port=config['dashboard']['port'],
        debug=False
    )
