"""
Windows Service Implementation
Triển khai dịch vụ Windows

Runs the Helmet Camera RF Receiver as a Windows Service
Chạy Máy thu Camera Mũ Bảo Hiểm RF như một dịch vụ Windows

Author: Helmet Camera RF System
License: MIT

Requirements:
- pywin32 (pip install pywin32)

Installation:
    python windows_service.py install

Start:
    python windows_service.py start

Stop:
    python windows_service.py stop

Remove:
    python windows_service.py remove
"""

import sys
import os
import logging
import time
from pathlib import Path

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
except ImportError:
    print("Error: pywin32 is not installed")
    print("Install it with: pip install pywin32")
    sys.exit(1)

# Setup logging
log_path = Path(__file__).parent.parent.parent / 'logs' / 'service.log'
log_path.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HelmetCameraService(win32serviceutil.ServiceFramework):
    """Windows Service for Helmet Camera RF Receiver"""
    
    _svc_name_ = "HelmetCameraService"
    _svc_display_name_ = "Helmet Camera RF Receiver"
    _svc_description_ = "RF video streaming receiver for helmet cameras. Provides multi-camera capture and web dashboard."
    
    def __init__(self, args):
        """Initialize the service"""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = False
        self.app = None
        
    def SvcStop(self):
        """Stop the service"""
        logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_running = False
        
    def SvcDoRun(self):
        """Run the service"""
        logger.info("=" * 60)
        logger.info("Helmet Camera RF Receiver Service Starting")
        logger.info("=" * 60)
        
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        self.is_running = True
        self.main()
        
    def main(self):
        """Main service loop"""
        try:
            # Import Flask app
            sys.path.insert(0, str(Path(__file__).parent))
            
            # Import required modules
            from flask import Flask
            from flask_socketio import SocketIO
            from flask_cors import CORS
            import yaml
            import threading
            
            # Import application modules
            from app import (
                app, socketio, config,
                initialize_system,
                telemetry_listener_task,
                channel_scanner_task,
                camera_monitor_task
            )
            
            logger.info("Initializing system components...")
            
            # Initialize without starting background tasks
            # (they will be started by initialize_system)
            os.makedirs('logs', exist_ok=True)
            os.makedirs(config['recording']['path'], exist_ok=True)
            
            # Start background tasks
            threading.Thread(target=telemetry_listener_task, daemon=True).start()
            threading.Thread(target=channel_scanner_task, daemon=True).start()
            threading.Thread(target=camera_monitor_task, daemon=True).start()
            
            logger.info("System initialized successfully")
            logger.info(f"Dashboard will be available at http://localhost:{config['dashboard']['port']}")
            
            # Run the Flask-SocketIO server in a separate thread
            def run_server():
                try:
                    socketio.run(
                        app,
                        host=config['dashboard']['host'],
                        port=config['dashboard']['port'],
                        debug=False,
                        use_reloader=False,
                        log_output=True
                    )
                except Exception as e:
                    logger.error(f"Server error: {e}")
                    self.SvcStop()
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            logger.info("Service is running")
            
            # Keep service running until stop event
            while self.is_running:
                # Wait for stop event (check every 5 seconds)
                rc = win32event.WaitForSingleObject(self.stop_event, 5000)
                if rc == win32event.WAIT_OBJECT_0:
                    break
            
            logger.info("Service stopping...")
            
        except Exception as e:
            logger.error(f"Service error: {e}", exc_info=True)
            servicemanager.LogErrorMsg(f"Service error: {e}")
        finally:
            logger.info("Service stopped")
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, '')
            )


def setup_service():
    """Setup service with additional configurations"""
    import win32api
    import win32con
    import win32service
    import winerror
    
    try:
        # Open service manager
        hscm = win32service.OpenSCManager(
            None,
            None,
            win32service.SC_MANAGER_ALL_ACCESS
        )
        
        try:
            # Open the service
            hs = win32service.OpenService(
                hscm,
                HelmetCameraService._svc_name_,
                win32service.SERVICE_ALL_ACCESS
            )
            
            try:
                # Configure service to restart on failure
                service_failure_actions = {
                    'ResetPeriod': 86400,  # 24 hours
                    'RebootMsg': u'',
                    'Command': u'',
                    'Actions': [
                        (win32service.SC_ACTION_RESTART, 30000),  # Restart after 30 seconds
                        (win32service.SC_ACTION_RESTART, 60000),  # Restart after 60 seconds
                        (win32service.SC_ACTION_RESTART, 120000), # Restart after 120 seconds
                    ]
                }
                
                win32service.ChangeServiceConfig2(
                    hs,
                    win32service.SERVICE_CONFIG_FAILURE_ACTIONS,
                    service_failure_actions
                )
                
                logger.info("Service configured to restart on failure")
                
            finally:
                win32service.CloseServiceHandle(hs)
        finally:
            win32service.CloseServiceHandle(hscm)
            
    except Exception as e:
        logger.warning(f"Could not configure service auto-restart: {e}")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Called by Windows Service Manager
        try:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(HelmetCameraService)
            servicemanager.StartServiceCtrlDispatcher()
        except Exception as e:
            logger.error(f"Failed to start service: {e}")
    else:
        # Called from command line
        if sys.argv[1] == 'install':
            # Install the service
            win32serviceutil.HandleCommandLine(HelmetCameraService)
            # Additional setup after installation
            try:
                setup_service()
                print("\n✅ Service installed successfully!")
                print("\nNext steps:")
                print("1. Start service: python windows_service.py start")
                print("2. Or use Windows Services: services.msc")
                print("\nService name: HelmetCameraService")
                print("Display name: Helmet Camera RF Receiver")
            except Exception as e:
                print(f"\n⚠️  Service installed but auto-restart configuration failed: {e}")
        else:
            # Handle other commands (start, stop, remove, etc.)
            win32serviceutil.HandleCommandLine(HelmetCameraService)
