#!/usr/bin/env python3
"""
ZapGaze Local Agent Launcher
Simple launcher that starts the agent and optionally sets up auto-start
"""

import os
import sys
import socket
from pathlib import Path


def check_port_available(port):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("localhost", port))
        sock.close()
        return True
    except OSError:
        return False


def start_agent():
    """Start the local agent server"""
    # Handle PyInstaller bundle vs regular script
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        # PyInstaller sets sys._MEIPASS to the temp folder
        bundle_dir = Path(sys._MEIPASS)
        # Add bundle directory to path
        sys.path.insert(0, str(bundle_dir))
        # Also add the directory containing the executable
        exe_dir = Path(sys.executable).parent
        sys.path.insert(0, str(exe_dir))
        project_root = exe_dir
    else:
        # Running as regular script
        agent_dir = Path(__file__).parent
        project_root = agent_dir.parent
        # Add parent directory to path so we can import app modules
        sys.path.insert(0, str(project_root))

    # Change to project root for proper imports
    os.chdir(project_root)

    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)

    # Get backend URL from environment or use default (Azure VM)
    backend_url = os.getenv("BACKEND_URL", "http://20.74.82.26:8000")
    env["BACKEND_URL"] = backend_url

    print("=" * 50)
    print("ZapGaze Local Agent")
    print("=" * 50)
    print(f"Backend URL: {backend_url}")
    print("Agent URL: http://localhost:9000")
    print("=" * 50)
    print("\nStarting agent...")
    print("Press Ctrl+C to stop\n")

    # Start uvicorn
    try:
        import uvicorn

        # Debug: Print sys.path to see what's available
        if getattr(sys, "frozen", False):
            print(f"🔍 PyInstaller bundle detected")
            print(f"   sys._MEIPASS: {sys._MEIPASS}")
            print(f"   sys.executable: {sys.executable}")
            print(f"   sys.path: {sys.path[:3]}...")  # First 3 entries

        # Import the app directly (works better with PyInstaller)
        try:
            # Try importing agent module first
            import agent

            print(f"✅ Imported agent module from: {agent.__file__}")
            from agent.local_agent import app

            print("✅ Successfully imported agent app")
            # Run with app object instead of string
            uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
        except ImportError as e:
            print(f"⚠️  Direct import failed: {e}")
            import traceback

            traceback.print_exc()
            print("\n   Trying alternative import methods...")
            # Try importing from the bundle directory
            try:
                if getattr(sys, "frozen", False):
                    # Add the bundle directory explicitly
                    bundle_path = Path(sys._MEIPASS)
                    if str(bundle_path) not in sys.path:
                        sys.path.insert(0, str(bundle_path))
                    # Try importing again
                    from agent.local_agent import app

                    print("✅ Imported from bundle directory")
                    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
                else:
                    raise
            except:
                print("   Trying string import as last resort...")
                # Fallback to string import if direct import fails
                uvicorn.run(
                    "agent.local_agent:app", host="0.0.0.0", port=9000, log_level="info"
                )
    except KeyboardInterrupt:
        print("\n\nAgent stopped.")
    except Exception as e:
        print(f"\nError starting agent: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point"""
    # Check for setup-autostart flag
    if len(sys.argv) > 1 and sys.argv[1] == "--setup-autostart":
        from agent.setup_autostart import main as setup_main

        setup_main()
        return

    # Check if port 9000 is available
    if not check_port_available(9000):
        print("⚠️  Port 9000 is already in use.")
        print("   Another instance of the agent may be running.")
        print("   Please stop it first or use a different port.")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != "y":
            sys.exit(1)

    # Start the agent
    start_agent()


if __name__ == "__main__":
    main()
