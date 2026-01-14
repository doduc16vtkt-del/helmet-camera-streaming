"""
Central Receiver Station - Backend API
Trạm tiếp nhận trung tâm - API Backend

Flask-based web server for receiving and managing RF camera feeds
Web server dựa trên Flask để nhận và quản lý luồng camera RF

Author:  Helmet Camera RF System
License:  MIT
"""

from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import yaml
import logging
import cv2
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

# Video Recording Class
# ============================================

class VideoRecorder:
    """Handle video recording for camera streams"""
    
    def __init__(self, camera_id, output_dir="./recordings"):
        self.camera_id = camera_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.writer = None
        self.recording = False
        self.filename = None
        self.start_time = None
        
    def start(self, fps=30, resolution=(1280, 720)):
        """Start recording"""
        if self.recording:
            logger.warning(f"Camera {self.camera_id} already recording")
            return False
        
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filename = self.output_dir / f"camera_{self.camera_id}_{timestamp}.mp4"
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'H264' if available
            self.writer = cv2.VideoWriter(
                str(self.filename),
                fourcc,
                fps,
                resolution
            )
            
            if not self.writer.isOpened():
                logger.error(f"Failed to open video writer for {self.filename}")
                return False
            
            self.recording = True
            self.start_time = datetime.now()
            
            logger.info(f"✅ Started recording camera {self.camera_id} to {self.filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting recording for camera {self.camera_id}:  {e}")
            return False
    
    def write_frame(self, frame):
        """Write a frame to video file"""
        if self.recording and self.writer:
            try:
                self.writer.write(frame)
                return True
            except Exception as e: 
                logger.error(f"Error writing frame:  {e}")
                return False
        return False
    
    def stop(self):
        """Stop recording"""
        if not self.recording:
            return False
        
        try: 
            self.recording = False
            
            if self.writer:
                self.writer.release()
                self.writer = None
            
            duration = (datetime.now() - self.start_time).total_seconds()
            file_size = self.filename.stat().st_size / (1024 * 1024)  # MB
            
            logger.info(f"✅ Stopped recording camera {self.camera_id}")
            logger.info(f"   File:  {self.filename}")
            logger.info(f"   Duration: {duration:.1f}s")
            logger.info(f"   Size: {file_size:.2f} MB")
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            return False
    
    def get_status(self):
        """Get recording status"""
        if self.recording and self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            return {
                'recording': True,
                'filename': str(self.filename. name),
                'duration': duration
            }
        return {'recording': False}


# Global recorders dictionary
camera_recorders = {}


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging. FileHandler('logs/receiver.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')
# Use environment variable or generate random secret key for production security
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ============================================
# Camera Streaming Components
# ============================================

# Global camera objects
camera_instances = {}
camera_lock = threading.Lock()

class SimpleCamera:
    """Simple camera wrapper for MJPEG streaming with error recovery"""
    def __init__(self, device_id=0):
        self.device_id = device_id
        self.cap = None
        self.running = False
        self.last_frame = None
        self. lock = threading.Lock()
        self.error_count = 0
        self.max_errors = 5  # Số lỗi liên tiếp trước khi restart
        self.last_successful_read = time.time()
        
    def start(self):
        """Start camera with MSMF backend"""
        try:
            logger.info(f"Starting camera {self.device_id} with MSMF backend...")
            
            # Use MSMF on Windows, default on Linux
            if platform.system() == 'Windows':
                self.cap = cv2.VideoCapture(self.device_id, cv2.CAP_MSMF)
            else:
                self.cap = cv2.VideoCapture(self.device_id)
            
            if not self. cap.isOpened():
                logger.error(f"Failed to open camera {self.device_id}")
                return False
            
            # CRITICAL: Read initial frame before setting properties
            ret, frame = self.cap.read()
            if not ret: 
                logger.error(f"Cannot capture initial frame from camera {self.device_id}")
                self.cap.release()
                return False
            
            logger.info(f"✅ Camera {self.device_id} initial frame:  {frame.shape}")
            
            # Optimize settings for stability
            try:
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # Small buffer (changed from 1)
                
                # Try to set MJPEG format
                try:
                    self.cap. set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                except: 
                    pass
                
                # Disable auto-exposure/focus if possible (helps stability)
                try:
                    self.cap. set(cv2.CAP_PROP_AUTOFOCUS, 0)
                    self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual mode
                except:
                    pass
                    
            except: 
                logger.warning(f"Could not set all properties for camera {self.device_id}")
            
            # Get actual settings
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            logger.info(f"Camera {self.device_id} settings: {width}x{height} @{fps}fps")
            
            self.running = True
            self.error_count = 0
            self.last_successful_read = time.time()
            
            # Start capture thread
            threading.Thread(target=self._capture_loop, daemon=True).start()
            
            logger.info(f"✅ Camera {self. device_id} started successfully")
            return True
            
        except Exception as e:
            logger. error(f"Error starting camera {self.device_id}: {e}")
            return False
    
    def _capture_loop(self):
        """Background thread to continuously capture frames with error recovery"""
        consecutive_errors = 0
        
        while self.running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                
                if ret:
                    # Successful read
                    with self.lock:
                        self.last_frame = frame
                    self.last_successful_read = time.time()
                    consecutive_errors = 0
                    self.error_count = 0
                else:
                    # Read failed
                    consecutive_errors += 1
                    self.error_count += 1
                    
                    # Log warning every 10 errors
                    if consecutive_errors % 10 == 1:
                        logger.warning(f"Camera {self.device_id}:  Failed to read frame (error count: {consecutive_errors})")
                    
                    # Check if camera is stuck
                    time_since_last_success = time.time() - self.last_successful_read
                    
                    if consecutive_errors >= self.max_errors or time_since_last_success > 5.0:
                        logger.error(f"Camera {self.device_id} appears stuck.  Attempting restart...")
                        
                        # Try to restart camera
                        if self._restart_camera():
                            logger.info(f"✅ Camera {self.device_id} restarted successfully")
                            consecutive_errors = 0
                        else:
                            logger.error(f"❌ Failed to restart camera {self.device_id}")
                            # Wait before retrying
                            time. sleep(2.0)
                    else:
                        # Short delay before retry
                        time. sleep(0.1)
            else:
                logger.error(f"Camera {self.device_id} not opened")
                time.sleep(1.0)
                
                # Try to reopen
                if not self._restart_camera():
                    time.sleep(5.0)  # Wait longer before next attempt
    
    def _restart_camera(self):
        """Restart camera (internal use)"""
        try:
            logger.info(f"Restarting camera {self.device_id}...")
            
            # Release old capture
            if self.cap:
                self.cap.release()
                time.sleep(0.5)  # Give time for release
            
            # Reopen camera
            if platform.system() == 'Windows':
                self.cap = cv2.VideoCapture(self.device_id, cv2.CAP_MSMF)
            else:
                self.cap = cv2.VideoCapture(self.device_id)
            
            if not self.cap.isOpened():
                return False
            
            # Read test frame
            ret, frame = self.cap.read()
            if not ret:
                self.cap.release()
                return False
            
            # Reset error counters
            self.error_count = 0
            self.last_successful_read = time.time()
            
            logger.info(f"✅ Camera {self.device_id} restart successful")
            return True
            
        except Exception as e: 
            logger.error(f"Error restarting camera {self.device_id}: {e}")
            return False
    
    def get_frame(self):
        """Get latest frame as JPEG bytes"""
        with self.lock:
            if self.last_frame is None:
                return None
            
            # Encode frame as JPEG
            ret, jpeg = cv2.imencode('.jpg', self.last_frame, 
                                     [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                return None
            
            return jpeg.tobytes()
    
    def stop(self):
        """Stop camera"""
        logger.info(f"Stopping camera {self.device_id}...")
        self.running = False
        time.sleep(0.3)  # Give thread time to finish
        
        if self.cap:
            self. cap.release()
        
        logger.info(f"Camera {self.device_id} stopped")
    
    def get_status(self):
        """Get camera status"""
        time_since_last = time.time() - self.last_successful_read
        
        return {
            'running': self.running,
            'error_count': self.error_count,
            'last_frame_age': time_since_last,
            'healthy': time_since_last < 2.0 and self.error_count < 10
        }

def generate_camera_frames(camera_id):
    """Generate frames for MJPEG stream"""
    while True:
        camera = camera_instances.get(camera_id)
        
        if camera and camera.running:
            frame_bytes = camera.get_frame()
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                time.sleep(0.03)  # 30fps
        else:
            time.sleep(0.1)

# ============================================
# Load Configuration
# ============================================

def load_config():
    """Load configuration from YAML file"""
    # Use os.path.join for cross-platform compatibility
    config_path = os.path.join('.. ', '.. ', 'configs', 'receiver_config.yaml')
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
        'capture': {
            'cameras': [
                {'id': 0, 'name': 'Camera 1', 'enabled': True},
            ]
        },
        'dashboard': {
            'host': '0.0.0.0',
            'port': 8080,
            'max_cameras': 8,
            'open_browser':  False
        },
        'recording': {
            'enabled': True,
            'path': './recordings',
            'format': 'mp4'
        }
    }

config = load_config()

# Initialize system components
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
        'active_cameras': len(camera_instances),
        'recording': len(system_state['recording_status']),
        'platform': platform.system()
    })

@app.route('/api/cameras')
def get_cameras():
    """Get list of active cameras"""
    cameras = []
    
    # Include streaming cameras
    for camera_id, camera in camera_instances.items():
        cameras.append({
            'device_id': f'camera_{camera_id}',
            'name': f'Camera {camera_id}',
            'status': 'online' if camera. running else 'offline',
            'stream_url': f'/camera_feed/{camera_id}',
            'recording': system_state['recording_status'].get(f'camera_{camera_id}', False),
        })
    
    # Include RF cameras from telemetry
    for device_id, camera_data in system_state['active_cameras'].items():
        if not any(c['device_id'] == device_id for c in cameras):
            cameras.append({
                'device_id': device_id,
                'channel': camera_data.get('channel'),
                'signal_strength': camera_data.get('rssi', 0),
                'battery': camera_data. get('battery_percent', 0),
                'recording': system_state['recording_status'].get(device_id, False),
                'last_seen': camera_data.get('last_seen', 0)
            })
    
    return jsonify({'cameras': cameras})

@app.route('/camera_feed/<int:camera_id>')
def camera_feed(camera_id):
    """Video streaming route for specific camera"""
    if camera_id not in camera_instances:
        return "Camera not found", 404
    
    return Response(
        generate_camera_frames(camera_id),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

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
            return jsonify({'success':  True, 'device_id': device_id})
        return jsonify({'success': False, 'error': 'Failed to start recording'}), 500
    except Exception as e:
        logger.error(f"Failed to start recording:  {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recording/stop/<device_id>', methods=['POST'])
def stop_recording(device_id):
    """Stop recording for a camera"""
    try:
        if storage_manager.stop_recording(device_id):
            system_state['recording_status'][device_id] = False
            socketio.emit('recording_stopped', {'device_id': device_id})
            return jsonify({'success': True, 'device_id': device_id})
        return jsonify({'success': False, 'error':  'Failed to stop recording'}), 500
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
        logger. error(f"Failed to set channel: {e}")
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
        'cameras': list(camera_instances.keys()),
        'platform': platform.system()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('request_video_frame')
def handle_video_request(data):
    """Handle video frame request"""
    device_id = data. get('device_id')
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
                    'rssi':  telemetry_data.get('rssi', 0),
                    'battery_percent': telemetry_data. get('battery_percent', 0),
                    'last_seen': time.time()
                }
                
                # Emit to connected clients
                socketio.emit('telemetry_update', {
                    'device_id': device_id,
                    'data': telemetry_data
                })
                
                logger.debug(f"Telemetry received from {device_id}")
                
        except Exception as e:
            logger.error(f"Error in telemetry listener:  {e}")
        
        time.sleep(0.1)  # Small delay to prevent busy loop

def channel_scanner_task():
    """Background task to scan RF channels"""
    logger.info("Starting channel scanner task")
    
    while True:
        try: 
            if config['receiver']. get('auto_switch', False):
                # Scan channels and switch to strongest signal
                channel_manager.scan_and_switch()
        except Exception as e:
            logger.error(f"Error in channel scanner: {e}")
        
        time.sleep(config['receiver']. get('scan_interval', 1000) / 1000.0)

def camera_monitor_task():
    """Monitor camera connections and clean up stale entries"""
    logger.info("Starting camera monitor task")
    
    while True:
        try: 
            current_time = time.time()
            stale_timeout = 10  # seconds
            
            # Check for stale cameras
            stale_cameras = []
            for device_id, camera_data in system_state['active_cameras']. items():
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

def initialize_cameras():
    """Initialize local USB cameras for streaming"""
    logger.info("Initializing local cameras...")
    
    # Get camera config
    camera_config = config. get('capture', {}).get('cameras', [])
    
    if not camera_config: 
        # Default:  try camera 0
        camera_config = [{'id': 0, 'name':  'Camera 0', 'enabled': True}]
    
    initialized_count = 0
    
    for cam_cfg in camera_config:
        if not cam_cfg.get('enabled', True):
            continue
        
        camera_id = cam_cfg['id']
        camera_name = cam_cfg.get('name', f'Camera {camera_id}')
        
        logger.info(f"Initializing {camera_name} (ID: {camera_id})...")
        
        camera = SimpleCamera(device_id=camera_id)
        if camera.start():
            camera_instances[camera_id] = camera
            initialized_count += 1
            logger.info(f"✅ {camera_name} initialized")
        else:
            logger. warning(f"⚠️ Failed to initialize {camera_name}")
    
    if initialized_count > 0:
        logger.info(f"✅ {initialized_count} camera(s) initialized for streaming")
    else:
        logger.warning("⚠️ No cameras initialized - streaming not available")
    
    return initialized_count

def initialize_system():
    """Initialize all system components"""
    logger.info("=" * 60)
    logger.info("Helmet Camera RF Receiver Station Starting")
    logger.info("Trạm Tiếp Nhận Camera Mũ Bảo Hiểm RF")
    logger.info("=" * 60)
    logger.info(f"Platform: {platform.system()}")
    
    # Create necessary directories (cross-platform)
    os.makedirs('logs', exist_ok=True)
    os.makedirs(config['recording']['path'], exist_ok=True)
    
    # Initialize local cameras for streaming
    initialize_cameras()
    
    # Initialize RF components
    if not rf_receiver.initialize():
        logger.warning("RF receiver not initialized (OK for USB camera testing)")
    
    if not telemetry_receiver.initialize():
        logger.warning("Telemetry receiver not initialized (OK for USB camera testing)")
    
    # Start background tasks
    threading.Thread(target=telemetry_listener_task, daemon=True).start()
    threading.Thread(target=channel_scanner_task, daemon=True).start()
    threading.Thread(target=camera_monitor_task, daemon=True).start()
    
    logger.info("System initialized successfully")
    logger.info(f"Dashboard available at http://0.0.0.0:{config['dashboard']['port']}")
    
    # Auto-launch browser on Windows if configured
    if platform.system() == 'Windows' and config. get('dashboard', {}).get('open_browser', False):
        import webbrowser
        port = config['dashboard']['port']
        url = f"http://localhost:{port}"
        logger.info(f"Auto-launching browser at {url}")
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()

# ============================================
# Main Entry Point / Điểm vào chính
# ============================================

if __name__ == '__main__': 
    try:
        initialize_system()
        
        # Run Flask-SocketIO server
        socketio. run(
            app,
            host=config['dashboard']['host'],
            port=config['dashboard']['port'],
            debug=False,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        logger. info("\nShutting down...")
        # Stop all cameras
        for camera in camera_instances.values():
            camera.stop()
        logger.info("✅ Shutdown complete")