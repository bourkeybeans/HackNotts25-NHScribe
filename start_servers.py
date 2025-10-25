#!/usr/bin/env python3
"""
Script to start both backend and frontend servers
"""
import subprocess
import sys
import os
import time
import threading

def run_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend server on http://localhost:8000")
    os.chdir('/Users/fin/HackNotts25/HackNotts25')
    subprocess.run([sys.executable, "-m", "uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])

def run_frontend():
    """Start the React frontend server"""
    print("🚀 Starting React frontend server on http://localhost:3000")
    os.chdir('/Users/fin/HackNotts25/HackNotts25/front-end')
    subprocess.run(["npm", "start"])

if __name__ == "__main__":
    print("🏥 NHScribe Development Environment")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n👋 Shutting down servers...")
        sys.exit(0)
