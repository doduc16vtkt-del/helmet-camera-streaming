/**
 * Dashboard JavaScript
 * JavaScript cho bảng điều khiển
 * 
 * Handles main dashboard functionality and WebSocket communication
 */

// Global state
let socket = null;
let cameras = {};
let systemUptime = 0;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard initializing...');
    initializeSocket();
    initializeControls();
    startUptimeCounter();
    refreshCameras();
});

/**
 * Initialize WebSocket connection
 */
function initializeSocket() {
    // Connect to Socket.IO server
    socket = io('http://localhost:8080', {
        transports: ['websocket', 'polling']
    });
    
    socket.on('connect', () => {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });
    
    socket.on('system_status', (data) => {
        console.log('System status:', data);
    });
    
    socket.on('telemetry_update', (data) => {
        console.log('Telemetry update:', data);
        updateCameraTelemetry(data.device_id, data.data);
    });
    
    socket.on('camera_disconnected', (data) => {
        console.log('Camera disconnected:', data.device_id);
        removeCameraItem(data.device_id);
    });
    
    socket.on('recording_started', (data) => {
        console.log('Recording started:', data.device_id);
        updateRecordingStatus(data.device_id, true);
    });
    
    socket.on('recording_stopped', (data) => {
        console.log('Recording stopped:', data.device_id);
        updateRecordingStatus(data.device_id, false);
    });
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (connected) {
        indicator.className = 'status-indicator connected';
        statusText.textContent = 'Connected / Đã kết nối';
    } else {
        indicator.className = 'status-indicator disconnected';
        statusText.textContent = 'Disconnected / Mất kết nối';
    }
}

/**
 * Initialize control handlers
 */
function initializeControls() {
    // Layout selector
    document.getElementById('layout-select').addEventListener('change', (e) => {
        const grid = document.getElementById('camera-grid');
        grid.className = 'camera-grid';
        if (e.target.value === 'single') {
            grid.classList.add('single');
        } else if (e.target.value === 'list') {
            grid.classList.add('list');
        }
    });
    
    // Grid columns
    document.getElementById('grid-columns').addEventListener('change', (e) => {
        const grid = document.getElementById('camera-grid');
        const columns = parseInt(e.target.value);
        grid.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
    });
    
    // Scan channels button
    document.getElementById('scan-channels-btn').addEventListener('click', () => {
        console.log('Scanning channels...');
        scanChannels();
    });
    
    // Refresh button
    document.getElementById('refresh-btn').addEventListener('click', () => {
        console.log('Refreshing cameras...');
        refreshCameras();
    });
}

/**
 * Refresh camera list from API
 */
async function refreshCameras() {
    try {
        const response = await fetch('/api/cameras');
        const data = await response.json();
        
        if (data.cameras && data.cameras.length > 0) {
            // Remove "no cameras" message
            const noCameras = document.querySelector('.no-cameras');
            if (noCameras) {
                noCameras.remove();
            }
            
            // Update cameras
            data.cameras.forEach(camera => {
                if (!cameras[camera.device_id]) {
                    addCameraItem(camera);
                } else {
                    updateCameraItem(camera);
                }
            });
            
            // Update statistics
            document.getElementById('active-cameras-count').textContent = data.cameras.length;
            
            // Count recording cameras
            const recordingCount = data.cameras.filter(c => c.recording).length;
            document.getElementById('recording-count').textContent = recordingCount;
        }
    } catch (error) {
        console.error('Failed to refresh cameras:', error);
    }
}

/**
 * Add a new camera item to the grid
 */
function addCameraItem(camera) {
    cameras[camera.device_id] = camera;
    
    const grid = document.getElementById('camera-grid');
    const item = document.createElement('div');
    item.className = 'camera-item';
    item.id = `camera-${camera.device_id}`;
    
    item.innerHTML = `
        <div class="camera-header">
            <div class="camera-id">${camera.device_id}</div>
            <div class="camera-status">
                <span class="status-badge online">ONLINE</span>
                ${camera.recording ? '<span class="status-badge recording">● REC</span>' : ''}
            </div>
        </div>
        <div class="camera-video">
            <canvas id="video-${camera.device_id}" width="640" height="480"></canvas>
        </div>
        <div class="camera-info">
            <div class="info-row">
                <span class="info-label">Channel / Kênh:</span>
                <span class="info-value">${camera.channel || 'N/A'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Signal / Tín hiệu:</span>
                <span class="info-value">${camera.signal_strength || 0} dBm</span>
            </div>
            <div class="signal-bar">
                <div class="signal-fill" style="width: ${getSignalPercent(camera.signal_strength)}%"></div>
            </div>
            <div class="info-row">
                <span class="info-label">Battery / Pin:</span>
                <span class="battery-indicator ${getBatteryClass(camera.battery)}">
                    ${camera.battery || 0}%
                </span>
            </div>
        </div>
        <div class="camera-controls">
            <button class="btn btn-record" onclick="toggleRecording('${camera.device_id}')">
                ${camera.recording ? '⏹ Stop' : '⏺ Record'}
            </button>
            <button class="btn btn-channel" onclick="selectChannel('${camera.device_id}')">
                📡 Channel
            </button>
        </div>
    `;
    
    grid.appendChild(item);
    
    // Initialize video player for this camera
    initializeVideoPlayer(camera.device_id);
}

/**
 * Update existing camera item
 */
function updateCameraItem(camera) {
    cameras[camera.device_id] = camera;
    
    const item = document.getElementById(`camera-${camera.device_id}`);
    if (!item) return;
    
    // Update signal strength
    const signalValue = item.querySelector('.info-row:nth-child(2) .info-value');
    if (signalValue) {
        signalValue.textContent = `${camera.signal_strength || 0} dBm`;
    }
    
    // Update signal bar
    const signalFill = item.querySelector('.signal-fill');
    if (signalFill) {
        signalFill.style.width = `${getSignalPercent(camera.signal_strength)}%`;
    }
    
    // Update battery
    const batteryIndicator = item.querySelector('.battery-indicator');
    if (batteryIndicator) {
        batteryIndicator.className = `battery-indicator ${getBatteryClass(camera.battery)}`;
        batteryIndicator.textContent = `${camera.battery || 0}%`;
    }
}

/**
 * Remove camera item from grid
 */
function removeCameraItem(deviceId) {
    const item = document.getElementById(`camera-${deviceId}`);
    if (item) {
        item.remove();
    }
    delete cameras[deviceId];
    
    // Show "no cameras" message if grid is empty
    const grid = document.getElementById('camera-grid');
    if (grid.children.length === 0) {
        grid.innerHTML = `
            <div class="no-cameras">
                <p>⏳ Waiting for cameras...</p>
                <p>Đang chờ camera...</p>
            </div>
        `;
    }
}

/**
 * Update camera telemetry data
 */
function updateCameraTelemetry(deviceId, data) {
    if (cameras[deviceId]) {
        cameras[deviceId].battery = data.battery_percent;
        cameras[deviceId].signal_strength = data.rssi;
        updateCameraItem(cameras[deviceId]);
    }
}

/**
 * Update recording status
 */
function updateRecordingStatus(deviceId, recording) {
    if (cameras[deviceId]) {
        cameras[deviceId].recording = recording;
        
        const item = document.getElementById(`camera-${deviceId}`);
        if (item) {
            const statusBadge = item.querySelector('.status-badge.recording');
            const recordBtn = item.querySelector('.btn-record');
            
            if (recording) {
                if (!statusBadge) {
                    const status = item.querySelector('.camera-status');
                    status.innerHTML += '<span class="status-badge recording">● REC</span>';
                }
                if (recordBtn) {
                    recordBtn.textContent = '⏹ Stop';
                }
            } else {
                if (statusBadge) {
                    statusBadge.remove();
                }
                if (recordBtn) {
                    recordBtn.textContent = '⏺ Record';
                }
            }
        }
    }
}

/**
 * Toggle recording for a camera
 */
async function toggleRecording(deviceId) {
    const camera = cameras[deviceId];
    if (!camera) return;
    
    const endpoint = camera.recording ? 'stop' : 'start';
    
    try {
        const response = await fetch(`/api/recording/${endpoint}/${deviceId}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            console.log(`Recording ${endpoint} for ${deviceId}`);
        } else {
            console.error(`Failed to ${endpoint} recording:`, data.error);
        }
    } catch (error) {
        console.error(`Error toggling recording:`, error);
    }
}

/**
 * Select channel for a camera
 */
function selectChannel(deviceId) {
    const channel = prompt('Enter channel (1-8) / Nhập kênh (1-8):', '1');
    if (channel && channel >= 1 && channel <= 8) {
        setChannel(deviceId, parseInt(channel));
    }
}

/**
 * Set RF channel for a camera
 */
async function setChannel(deviceId, channel) {
    try {
        const response = await fetch(`/api/channel/set/${deviceId}/${channel}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            console.log(`Channel set to ${channel} for ${deviceId}`);
            refreshCameras();
        }
    } catch (error) {
        console.error('Error setting channel:', error);
    }
}

/**
 * Scan all channels
 */
async function scanChannels() {
    // Implementation would trigger channel scanning
    console.log('Channel scanning not yet implemented');
}

/**
 * Convert RSSI to percentage
 */
function getSignalPercent(rssi) {
    // Convert dBm to percentage (rough estimate)
    // -50 dBm = 100%, -90 dBm = 0%
    if (!rssi) return 0;
    const percent = ((rssi + 90) / 40) * 100;
    return Math.max(0, Math.min(100, percent));
}

/**
 * Get battery level CSS class
 */
function getBatteryClass(battery) {
    if (!battery) return 'low';
    if (battery >= 60) return 'high';
    if (battery >= 30) return 'medium';
    return 'low';
}

/**
 * Start uptime counter
 */
function startUptimeCounter() {
    setInterval(() => {
        systemUptime++;
        const hours = Math.floor(systemUptime / 3600);
        const minutes = Math.floor((systemUptime % 3600) / 60);
        const seconds = systemUptime % 60;
        
        const uptimeText = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        document.getElementById('system-uptime').textContent = uptimeText;
    }, 1000);
}

// Auto-refresh cameras every 5 seconds
setInterval(refreshCameras, 5000);
