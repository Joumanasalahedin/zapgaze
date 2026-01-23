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
    if getattr(sys, "frozen", False):
        bundle_dir = Path(sys._MEIPASS)
        sys.path.insert(0, str(bundle_dir))
        exe_dir = Path(sys.executable).parent
        sys.path.insert(0, str(exe_dir))
        project_root = exe_dir
    else:
        agent_dir = Path(__file__).parent
        project_root = agent_dir.parent
        sys.path.insert(0, str(project_root))

    os.chdir(project_root)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)

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

    try:
        import uvicorn

        if getattr(sys, "frozen", False):
            print(f"🔍 PyInstaller bundle detected")
            print(f"   sys._MEIPASS: {sys._MEIPASS}")
            print(f"   sys.executable: {sys.executable}")
            print(f"   sys.path: {sys.path[:3]}...")  # First 3 entries

        try:
            import agent

            print(f"✅ Imported agent module from: {agent.__file__}")
            from agent.local_agent import app

            print("✅ Successfully imported agent app")
            uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
        except ImportError as e:
            print(f"⚠️  Direct import failed: {e}")
            import traceback

            traceback.print_exc()
            print("\n   Trying alternative import methods...")
            try:
                if getattr(sys, "frozen", False):
                    bundle_path = Path(sys._MEIPASS)
                    if str(bundle_path) not in sys.path:
                        sys.path.insert(0, str(bundle_path))
                    from agent.local_agent import app

                    print("✅ Imported from bundle directory")
                    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
                else:
                    raise
            except:
                print("   Trying string import as last resort...")
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
    if len(sys.argv) > 1 and sys.argv[1] == "--setup-autostart":
        from agent.setup_autostart import main as setup_main

        setup_main()
        return

    if not check_port_available(9000):
        print("⚠️  Port 9000 is already in use.")
        print("   Another instance of the agent may be running.")
        print("   Please stop it first or use a different port.")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != "y":
            sys.exit(1)

    start_agent()


if __name__ == "__main__":
    main()
