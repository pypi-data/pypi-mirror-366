import subprocess
import sys
from pathlib import Path

import re

def list_ssh_hosts(ssh_config_path: Path):
    if not ssh_config_path.exists():
        print(f"❌ SSH config file not found: {ssh_config_path}")
        return

    print("📜 SSH Hosts:")
    print(f"{'Name':<20} {'HostName':<20} {'Jump':<20}")
    print("-" * 60)

    hosts = []
    current = {}
    with open(ssh_config_path) as f:
        for line in f:
            line = line.strip()
            if line.lower().startswith("host ") and not line.lower().startswith("host *"):
                if current:
                    hosts.append(current)
                    current = {}
                current["Host"] = line.split()[1]
            elif line.lower().startswith("hostname "):
                current["HostName"] = line.split()[1]
            elif line.lower().startswith("proxyjump "):
                current["ProxyJump"] = line.split()[1]

        if current:
            hosts.append(current)

    for entry in hosts:
        print(f"{entry.get('Host',''):<20} {entry.get('HostName',''):<20} {entry.get('ProxyJump',''):<20}")

def main():
    ssh_config = Path.home() / ".ssh" / "config"
    script_path = Path(__file__).parent / "rbash.sh"

    if not script_path.exists():
        print(f"❌ Error: {script_path} not found.")
        sys.exit(1)

    if len(sys.argv) == 1:
        list_ssh_hosts(ssh_config)
        sys.exit(0)

    host = sys.argv[1]
    cmd = ["bash", str(script_path), "run", host]
    print(f"🔧 Running: {' '.join(cmd)}")

    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"❌ Script failed with code {e.returncode}")
        sys.exit(e.returncode)