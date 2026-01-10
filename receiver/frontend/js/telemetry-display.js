/**
 * Telemetry Display Module
 * Module hiển thị telemetry
 * 
 * Handles display of telemetry data and alerts
 */

const telemetryData = {};

/**
 * Update telemetry display for a camera
 */
function updateTelemetryDisplay(deviceId, data) {
    telemetryData[deviceId] = data;
    
    // Update battery indicator
    updateBatteryDisplay(deviceId, data.battery_percent);
    
    // Update signal strength
    updateSignalDisplay(deviceId, data.rssi);
    
    // Update temperature if available
    if (data.temperature) {
        updateTemperatureDisplay(deviceId, data.temperature);
    }
    
    // Check for low battery alert
    if (data.battery_percent < 20) {
        showAlert(deviceId, 'low-battery', 'Low Battery / Pin Yếu');
    }
    
    // Check for weak signal alert
    if (data.rssi < -85) {
        showAlert(deviceId, 'weak-signal', 'Weak Signal / Tín Hiệu Yếu');
    }
}

/**
 * Update battery display
 */
function updateBatteryDisplay(deviceId, percent) {
    const item = document.getElementById(`camera-${deviceId}`);
    if (!item) return;
    
    const batteryIndicator = item.querySelector('.battery-indicator');
    if (batteryIndicator) {
        batteryIndicator.className = `battery-indicator ${getBatteryClass(percent)}`;
        batteryIndicator.textContent = `${percent}%`;
    }
}

/**
 * Update signal strength display
 */
function updateSignalDisplay(deviceId, rssi) {
    const item = document.getElementById(`camera-${deviceId}`);
    if (!item) return;
    
    const signalValue = item.querySelector('.info-row:nth-child(2) .info-value');
    if (signalValue) {
        signalValue.textContent = `${rssi} dBm`;
    }
    
    const signalFill = item.querySelector('.signal-fill');
    if (signalFill) {
        const percent = getSignalPercent(rssi);
        signalFill.style.width = `${percent}%`;
        
        // Update color based on strength
        if (percent < 30) {
            signalFill.className = 'signal-fill weak';
        } else if (percent < 60) {
            signalFill.className = 'signal-fill medium';
        } else {
            signalFill.className = 'signal-fill';
        }
    }
}

/**
 * Update temperature display
 */
function updateTemperatureDisplay(deviceId, temperature) {
    const item = document.getElementById(`camera-${deviceId}`);
    if (!item) return;
    
    // Check if temperature row exists
    let tempRow = item.querySelector('.temp-row');
    if (!tempRow) {
        // Create temperature row
        const cameraInfo = item.querySelector('.camera-info');
        tempRow = document.createElement('div');
        tempRow.className = 'info-row temp-row';
        tempRow.innerHTML = `
            <span class="info-label">Temperature / Nhiệt độ:</span>
            <span class="info-value">${temperature.toFixed(1)}°C</span>
        `;
        cameraInfo.appendChild(tempRow);
    } else {
        // Update existing row
        const tempValue = tempRow.querySelector('.info-value');
        if (tempValue) {
            tempValue.textContent = `${temperature.toFixed(1)}°C`;
        }
    }
}

/**
 * Show alert for a camera
 */
function showAlert(deviceId, alertType, message) {
    // Create alert if it doesn't exist
    const alertId = `alert-${deviceId}-${alertType}`;
    if (document.getElementById(alertId)) return; // Alert already shown
    
    const item = document.getElementById(`camera-${deviceId}`);
    if (!item) return;
    
    const alert = document.createElement('div');
    alert.id = alertId;
    alert.className = `alert alert-${alertType}`;
    alert.textContent = message;
    alert.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: #f44336;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 10;
        animation: fadeIn 0.3s;
    `;
    
    const videoContainer = item.querySelector('.camera-video');
    if (videoContainer) {
        videoContainer.style.position = 'relative';
        videoContainer.appendChild(alert);
        
        // Auto-remove alert after 10 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 10000);
    }
}

/**
 * Clear all alerts for a camera
 */
function clearAlerts(deviceId) {
    const item = document.getElementById(`camera-${deviceId}`);
    if (!item) return;
    
    const alerts = item.querySelectorAll('.alert');
    alerts.forEach(alert => alert.remove());
}

/**
 * Get telemetry history for a camera
 */
async function getTelemetryHistory(deviceId) {
    try {
        const response = await fetch(`/api/telemetry/${deviceId}`);
        const data = await response.json();
        
        if (data) {
            updateTelemetryDisplay(deviceId, data);
        }
    } catch (error) {
        console.error(`Failed to get telemetry for ${deviceId}:`, error);
    }
}

/**
 * Format uptime as human-readable string
 */
function formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}
