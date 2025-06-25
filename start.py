#!/usr/bin/env python3
"""
Startup script for the AI Course Management Agent.
This script handles setup, validation, and launches the application.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_environment_file():
    """Check if .env file exists and has required keys."""
    env_file = Path(".env")
    example_file = Path("config.env.example")
    
    if not env_file.exists():
        if example_file.exists():
            print("⚠️  .env file not found")
            print("📝 Creating .env from config.env.example...")
            
            # Copy example file to .env
            with open(example_file, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            
            print("✅ .env file created")
            print("⚠️  Please edit .env file with your API keys before running")
            return False
        else:
            print("❌ No .env or config.env.example file found")
            return False
    
    # Load and check environment variables
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    has_keys = False
    
    if openai_key and openai_key != 'your_openai_api_key_here':
        print("✅ OpenAI API key configured")
        has_keys = True
    else:
        print("⚠️  OpenAI API key not configured")
    
    if google_key and google_key != 'your_google_api_key_here':
        print("✅ Google AI API key configured")
        has_keys = True
    else:
        print("⚠️  Google AI API key not configured")
    
    if not has_keys:
        print("\n💡 At least one AI provider API key is required:")
        print("   • Get OpenAI API key: https://platform.openai.com/api-keys")
        print("   • Get Google AI API key: https://makersuite.google.com/app/apikey")
        print("   • Edit .env file with your keys")
        return False
    
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        # Try importing key dependencies
        import fastapi
        import uvicorn
        import openai
        import google.generativeai
        import pydantic
        print("✅ Core dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Installing dependencies...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("💡 Try running: pip install -r requirements.txt")
            return False


def run_tests():
    """Run basic system tests."""
    print("\n🧪 Running basic system tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_agent.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ System tests passed")
            return True
        else:
            print("❌ System tests failed")
            print("Output:", result.stdout[-500:])  # Last 500 chars
            if result.stderr:
                print("Errors:", result.stderr[-500:])
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Tests timed out")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


def start_server(host="localhost", port=8001, reload=True):
    """Start the FastAPI server."""
    print(f"\n🚀 Starting AI Course Management Agent...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Reload: {reload}")
    print(f"   URL: http://{host}:{port}")
    print(f"   Docs: http://{host}:{port}/docs")
    print("\n⌨️  Press Ctrl+C to stop the server")
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")


def print_usage_info():
    """Print usage information."""
    print("\n📚 Usage Information:")
    print("   • API Documentation: http://localhost:8001/docs")
    print("   • Health Check: http://localhost:8001/health")
    print("   • Available Tools: http://localhost:8001/api/v1/tools")
    print("   • Test Examples: python example_usage.py")
    print("   • System Tests: python test_agent.py")


def main():
    """Main startup sequence."""
    print("🤖 AI Course Management Agent - Startup")
    print("=" * 50)
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Check environment setup
    print("\n🔧 Checking environment setup...")
    if not check_environment_file():
        print("\n💡 Setup .env file with API keys and run again")
        sys.exit(1)
    
    # Step 3: Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Step 4: Run tests (optional, skip if fails)
    # test_passed = run_tests()
    # if not test_passed:
    #     print("⚠️  Tests failed, but continuing anyway...")
    #     print("   You can still use the system, but some features may not work")
    
    # Step 5: Print usage info
    print_usage_info()
    
    # Step 6: Start server
    try:
        # Get configuration from environment
        load_dotenv()
        host = os.getenv('API_HOST', 'localhost')
        port = int(os.getenv('API_PORT', 8001))
        
        start_server(host=host, port=8001)
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 