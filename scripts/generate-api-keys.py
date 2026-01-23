#!/usr/bin/env python3
"""
Generate secure API keys for ZapGaze
Usage: python scripts/generate-api-keys.py
"""

import secrets
import sys
import os


def generate_api_key(length=32):
    """Generate a secure random API key"""
    return secrets.token_urlsafe(length)


def main():
    print("=" * 60)
    print("ZapGaze API Key Generator")
    print("=" * 60)
    print()

    # Generate keys
    agent_key = generate_api_key()
    frontend_key = generate_api_key()

    print("Generated API Keys:")
    print("-" * 60)
    print(f"AGENT_API_KEY={agent_key}")
    print(f"FRONTEND_API_KEY={frontend_key}")
    print("-" * 60)
    print()

    # Create .env file
    env_file = ".env"
    env_example_file = ".env.example"

    # Check if .env already exists
    if os.path.exists(env_file):
        response = input(f"{env_file} already exists. Overwrite? (y/n): ")
        if response.lower() != "y":
            print("Cancelled. Keys generated above but not saved.")
            return

    # Write .env file
    with open(env_file, "w") as f:
        f.write("# ZapGaze API Keys\n")
        f.write("# Generated automatically - DO NOT COMMIT TO GIT\n")
        f.write(f"AGENT_API_KEY={agent_key}\n")
        f.write(f"FRONTEND_API_KEY={frontend_key}\n")

    print(f"✅ Saved to {env_file}")
    print()

    # Create .env.example file
    with open(env_example_file, "w") as f:
        f.write("# ZapGaze API Keys\n")
        f.write("# Copy this file to .env and set your keys\n")
        f.write("AGENT_API_KEY=your-agent-api-key-here\n")
        f.write("FRONTEND_API_KEY=your-frontend-api-key-here\n")

    print(f"✅ Created {env_example_file} (template file)")
    print()

    # Create agent_config.py for embedding in agent
    agent_config_file = "agent/agent_config.py"
    with open(agent_config_file, "w") as f:
        f.write('"""\n')
        f.write("Agent configuration - API key embedded at build time\n")
        f.write("This file is generated automatically. DO NOT EDIT MANUALLY.\n")
        f.write('"""\n')
        f.write("\n")
        f.write("# API Key for backend authentication\n")
        f.write("# This key is embedded in the agent executable at build time\n")
        f.write(f'AGENT_API_KEY = "{agent_key}"\n')
        f.write("\n")
        f.write(
            "# For development/testing, you can override with environment variable\n"
        )
        f.write("import os\n")
        f.write('AGENT_API_KEY = os.getenv("AGENT_API_KEY", AGENT_API_KEY)\n')

    print(f"✅ Created {agent_config_file} (embedded in agent executable)")
    print()

    print("=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Set environment variables on Azure VM:")
    print(f"   export AGENT_API_KEY={agent_key}")
    print(f"   export FRONTEND_API_KEY={frontend_key}")
    print()
    print("2. Rebuild agent executable:")
    print("   cd agent && ./build.sh")
    print()
    print("3. The agent will automatically use the embedded key")
    print("   (no user configuration needed!)")
    print()
    print("⚠️  IMPORTANT:")
    print("   - Add .env to .gitignore (if not already)")
    print("   - Do NOT commit .env or agent/agent_config.py to git")
    print("   - Keep these keys secret!")
    print()


if __name__ == "__main__":
    main()
