import subprocess
import sys, time
from pathlib import Path
import importlib.resources

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

    if len(sys.argv) == 1:
        list_ssh_hosts(ssh_config)
        sys.exit(0)

    host = sys.argv[1]
#    print(f"🔧 Running: {' '.join(cmd)}")
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            # Get path to bundled rbash.sh
            with importlib.resources.path("rbash", "rbash.sh") as script_path:
                print(f"🔧 Running: bash {script_path}")
                cmd = ["bash", str(script_path), "run", host]
                subprocess.check_call(cmd)
            break
        except KeyboardInterrupt:
            print("\n🔴 Script interrupted by user.")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"❌ Script failed with code {e.returncode}")
            retries += 1
            if retries < max_retries:
                print(f"🔄 Retrying... ({retries}/{max_retries})")
                time.sleep(5)
            else:
                sys.exit(e.returncode)
        finally:
            with importlib.resources.path("rbash", "rbash.sh") as script_path:
                cmd = ["bash", str(script_path), "clean", host]
                try:
                    subprocess.check_call(cmd)
                except:
                    pass
            print("🧽 Cleanup successful.")