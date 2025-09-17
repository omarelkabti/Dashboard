#!/usr/bin/env python3
"""
Fixed dashboard starter - automatically finds available port
"""

import subprocess
import sys
import socket
import webbrowser
import time
import threading

def find_free_port():
    """Find an available port starting from 8501"""
    for port in range(8501, 8510):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                continue
    return 8501  # fallback

def open_browser_delayed(port):
    """Open browser after a delay"""
    time.sleep(4)
    webbrowser.open(f'http://localhost:{port}')

def main():
    print("🎯 PET Resource Allocation Dashboard - Auto Port")
    print("=" * 60)
    
    # Find available port
    port = find_free_port()
    print(f"🔗 Starting dashboard on port {port}")
    print(f"📊 URL: http://localhost:{port}")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    
    # Start browser opener in background
    browser_thread = threading.Thread(target=open_browser_delayed, args=(port,))
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', str(port),
            '--server.headless', 'false',
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")

if __name__ == "__main__":
    main()
