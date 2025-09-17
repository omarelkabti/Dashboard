#!/usr/bin/env python3
"""
Quick start script for PET Resource Allocation Dashboard
Run this to automatically start the Streamlit dashboard
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_python():
    """Check if Python 3 is available"""
    try:
        result = subprocess.run([sys.executable, '--version'], 
                              capture_output=True, text=True)
        print(f"✅ Python version: {result.stdout.strip()}")
        return True
    except:
        print("❌ Python 3 not found")
        return False

def install_requirements():
    """Install required packages"""
    print("🔄 Installing required packages...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        print("💡 Try running: pip install streamlit pandas plotly")
        return False

def check_data_files():
    """Check if data files exist"""
    data_dir = Path('data')
    if not data_dir.exists():
        print("❌ Data directory not found")
        return False
    
    csv_files = list(data_dir.glob('*.csv'))
    if not csv_files:
        print("❌ No CSV files found in data directory")
        print("💡 Please add your PET Resource Allocation CSV files to the data/ folder")
        return False
    
    latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
    print(f"✅ Found data file: {latest_file.name}")
    return True

def start_streamlit():
    """Start the Streamlit dashboard"""
    print("\n🚀 Starting PET Resource Allocation Dashboard...")
    print("📊 Dashboard will open in your browser automatically")
    print("🔗 URL: http://localhost:8501")
    print("\n⚡ To stop the dashboard, press Ctrl+C in this terminal")
    print("=" * 60)
    
    # Give user a moment to read the message
    time.sleep(2)
    
    # Start Streamlit
    try:
        # Try to open browser after a short delay
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:8501')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.headless', 'false',
            '--server.port', '8501',
            '--browser.gatherUsageStats', 'false'
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("💡 Try running manually: streamlit run app.py")

def main():
    """Main setup and start function"""
    print("🎯 PET Resource Allocation Dashboard - Quick Start")
    print("=" * 60)
    
    # Check prerequisites
    if not check_python():
        return
    
    if not check_data_files():
        return
    
    # Install packages
    if not install_requirements():
        print("💡 Manual installation command:")
        print("   pip install streamlit pandas plotly")
        response = input("\n❓ Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Start dashboard
    start_streamlit()

if __name__ == "__main__":
    main()
