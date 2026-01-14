# Save as: receiver/backend/camera_stream_server.py
"""
Simple camera streaming server for testing
"""
from flask import Flask, Response, render_template_string
import cv2
import threading
import time

app = Flask(__name__)

# Global camera object
camera = None
camera_lock = threading.Lock()

class Camera:
    """Simple MSMF camera wrapper"""
    def __init__(self, device_id=0):
        self.device_id = device_id
        self.cap = None
        self. running = False
        
    def start(self):
        """Start camera"""
        self.cap = cv2.VideoCapture(self.device_id, cv2.CAP_MSMF)
        
        if not self.cap.isOpened():
            print(f"❌ Failed to open camera {self.device_id}")
            return False
        
        # Read first frame
        ret, _ = self.cap.read()
        if not ret:
            print("❌ Cannot capture frame")
            self.cap. release()
            return False
        
        self.running = True
        print(f"✅ Camera {self.device_id} started")
        return True
    
    def get_frame(self):
        """Get JPEG frame"""
        if not self.running:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Encode as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret: 
            return None
        
        return jpeg.tobytes()
    
    def stop(self):
        """Stop camera"""
        self.running = False
        if self.cap:
            self.cap.release()

def generate_frames():
    """Generate frames for MJPEG stream"""
    global camera
    
    while True:
        if camera and camera.running:
            frame = camera.get_frame()
            if frame:
                # MJPEG format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.1)

@app.route('/')
def index():
    """Main page with video player"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Camera Stream Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding:  20px;
                background: #1a1a1a;
                color: #fff;
            }
            h1 {
                text-align: center;
                color: #4CAF50;
            }
            .video-container {
                text-align: center;
                margin: 20px 0;
                background: #000;
                padding: 20px;
                border-radius: 10px;
            }
            img {
                max-width: 100%;
                border:  2px solid #4CAF50;
                border-radius: 5px;
            }
            . info {
                background: #2a2a2a;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .status {
                display: inline-block;
                padding: 5px 15px;
                background: #4CAF50;
                border-radius: 20px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h1>🎥 Camera Stream Test</h1>
        
        <div class="info">
            <p><span class="status">● LIVE</span> Camera 0 - MSMF Backend</p>
            <p>Resolution: 640x480 | FPS: ~30</p>
        </div>
        
        <div class="video-container">
            <img src="/video_feed" alt="Camera Stream">
        </div>
        
        <div class="info">
            <h3>✅ Camera Working!</h3>
            <p>Backend:  Media Foundation (MSMF)</p>
            <p>Platform: Windows</p>
            <p>Stream Format: MJPEG over HTTP</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

def initialize_camera():
    """Initialize camera on startup"""
    global camera
    
    print("="*60)
    print("CAMERA STREAM SERVER")
    print("="*60)
    
    camera = Camera(device_id=0)
    
    if not camera.start():
        print("❌ Failed to start camera")
        return False
    
    print("✅ Camera initialized")
    return True

if __name__ == '__main__':
    if initialize_camera():
        print(f"\n🚀 Server starting on http://localhost:5000")
        print("Open browser and go to:   http://localhost:5000\n")
        
        try: 
            app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        finally:
            if camera:
                camera.stop()
    else:
        print("❌ Server startup failed")