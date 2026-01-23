#!/usr/bin/env python3
"""
Auto-start setup script for ZapGaze Local Agent
Sets up the agent to start automatically on system login
"""

import os
import sys
import platform
from pathlib import Path


def setup_macos_autostart(agent_path):
    """Set up auto-start on macOS using LaunchAgent"""
    home = Path.home()
    launch_agents_dir = home / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)

    plist_file = launch_agents_dir / "com.zapgaze.agent.plist"

    python_path = sys.executable
    agent_abs_path = str(Path(agent_path).resolve())

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.zapgaze.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{agent_abs_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{home}/Library/Logs/zapgaze-agent.log</string>
    <key>StandardErrorPath</key>
    <string>{home}/Library/Logs/zapgaze-agent-error.log</string>
</dict>
</plist>"""

    plist_file.write_text(plist_content)
    print("✅ Auto-start configured for macOS")
    print(f"   LaunchAgent file: {plist_file}")
    print(f"   To test: launchctl load {plist_file}")
    return True


def setup_windows_autostart(agent_path):
    """Set up auto-start on Windows using Task Scheduler or Startup folder"""
    startup_folder = (
        Path(os.getenv("APPDATA"))
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
    )
    startup_folder.mkdir(parents=True, exist_ok=True)

    batch_file = startup_folder / "ZapGazeAgent.bat"
    agent_abs_path = str(Path(agent_path).resolve())
    python_path = sys.executable

    batch_content = f'@echo off\nstart "" "{python_path}" "{agent_abs_path}"\n'
    batch_file.write_text(batch_content)

    print("✅ Auto-start configured for Windows")
    print(f"   Startup script: {batch_file}")
    return True


def setup_linux_autostart(agent_path):
    """Set up auto-start on Linux using systemd user service or autostart"""
    home = Path.home()

    systemd_user_dir = home / ".config" / "systemd" / "user"
    systemd_user_dir.mkdir(parents=True, exist_ok=True)

    service_file = systemd_user_dir / "zapgaze-agent.service"
    agent_abs_path = str(Path(agent_path).resolve())
    python_path = sys.executable

    service_content = f"""[Unit]
Description=ZapGaze Local Agent
After=network.target

[Service]
Type=simple
ExecStart={python_path} {agent_abs_path}
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
"""

    service_file.write_text(service_content)

    autostart_dir = home / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)

    desktop_file = autostart_dir / "zapgaze-agent.desktop"
    desktop_content = f"""[Desktop Entry]
Type=Application
Name=ZapGaze Agent
Exec={python_path} {agent_abs_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""

    desktop_file.write_text(desktop_content)
    desktop_file.chmod(0o755)

    print("✅ Auto-start configured for Linux")
    print(f"   Systemd service: {service_file}")
    print(f"   Autostart file: {desktop_file}")
    print("   To enable: systemctl --user enable zapgaze-agent.service")
    return True


def main():
    """Main setup function"""
    system = platform.system()

    if getattr(sys, "frozen", False):
        agent_path = sys.executable
    else:
        agent_path = Path(__file__).parent / "launcher.py"

    print("=" * 50)
    print("ZapGaze Agent - Auto-start Setup")
    print("=" * 50)
    print(f"System: {system}")
    print(f"Agent path: {agent_path}")
    print()

    try:
        if system == "Darwin":
            setup_macos_autostart(agent_path)
        elif system == "Windows":
            setup_windows_autostart(agent_path)
        elif system == "Linux":
            setup_linux_autostart(agent_path)
        else:
            print(f"❌ Unsupported system: {system}")
            return False

        print("\n✅ Auto-start setup complete!")
        print("   The agent will start automatically when you log in.")
        return True

    except Exception as e:
        print(f"\n❌ Error setting up auto-start: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
