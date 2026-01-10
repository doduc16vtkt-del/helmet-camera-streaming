/**
 * Video Player Module
 * Module phát video
 * 
 * Handles video streaming and display for each camera
 */

const videoPlayers = {};

/**
 * Initialize video player for a camera
 */
function initializeVideoPlayer(deviceId) {
    const canvas = document.getElementById(`video-${deviceId}`);
    if (!canvas) {
        console.error(`Canvas not found for ${deviceId}`);
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    videoPlayers[deviceId] = {
        canvas: canvas,
        ctx: ctx,
        active: true,
        lastFrame: null
    };
    
    // Start requesting frames
    requestVideoFrames(deviceId);
    
    console.log(`Video player initialized for ${deviceId}`);
}

/**
 * Request video frames from server
 */
function requestVideoFrames(deviceId) {
    const player = videoPlayers[deviceId];
    if (!player || !player.active) return;
    
    // Request frame via WebSocket
    if (socket && socket.connected) {
        socket.emit('request_video_frame', { device_id: deviceId });
    }
    
    // Continue requesting frames
    setTimeout(() => requestVideoFrames(deviceId), 33); // ~30 fps
}

/**
 * Display video frame on canvas
 */
function displayVideoFrame(deviceId, frameData) {
    const player = videoPlayers[deviceId];
    if (!player) return;
    
    const img = new Image();
    img.onload = function() {
        player.ctx.drawImage(img, 0, 0, player.canvas.width, player.canvas.height);
    };
    img.src = `data:image/jpeg;base64,${frameData}`;
}

/**
 * Stop video player
 */
function stopVideoPlayer(deviceId) {
    if (videoPlayers[deviceId]) {
        videoPlayers[deviceId].active = false;
        delete videoPlayers[deviceId];
    }
}

/**
 * Draw placeholder on canvas (no signal)
 */
function drawNoSignal(deviceId) {
    const player = videoPlayers[deviceId];
    if (!player) return;
    
    player.ctx.fillStyle = '#000';
    player.ctx.fillRect(0, 0, player.canvas.width, player.canvas.height);
    
    player.ctx.fillStyle = '#888';
    player.ctx.font = '24px Arial';
    player.ctx.textAlign = 'center';
    player.ctx.textBaseline = 'middle';
    player.ctx.fillText('No Signal', player.canvas.width / 2, player.canvas.height / 2 - 20);
    player.ctx.fillText('Không Tín Hiệu', player.canvas.width / 2, player.canvas.height / 2 + 20);
}

// Handle incoming video frames
if (socket) {
    socket.on('video_frame', (data) => {
        displayVideoFrame(data.device_id, data.frame);
    });
}
